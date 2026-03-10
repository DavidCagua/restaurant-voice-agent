from dotenv import load_dotenv
import asyncio
import json
import os
import re
import time
import uuid

from num2words import num2words

from livekit import agents
from livekit.agents.telemetry import set_tracer_provider
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool
from livekit.agents import llm
from livekit.agents.voice import ModelSettings
from typing import AsyncIterable
from livekit import rtc
from livekit.plugins import (
    openai,
    elevenlabs,
    deepgram,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from restaurant_tools import (
    get_menu,
    get_categories,
    create_order,
    format_menu_for_voice,
)
from src.observability import get_observability_context, ObservabilityContext
from src.health import start_health_server
from src.retry import async_retry_with_backoff

load_dotenv()

# Spanish digit names for phone numbers (digit-by-digit)
_DIGITS_ES = ("cero", "uno", "dos", "tres", "cuatro", "cinco", "seis", "siete", "ocho", "nueve")


def _normalize_numbers_for_tts(text: str) -> str:
    """Convert numbers to spoken Spanish. Phone (10-11 digits) → digit-by-digit; others → words."""
    if not text.strip():
        return text

    def replace_phone(m):
        digits = re.sub(r"\D", "", m.group(0))
        if len(digits) in (10, 11):  # Phone numbers only
            return " ".join(_DIGITS_ES[int(d)] for d in digits)
        return m.group(0)

    def replace_number(m):
        s = m.group(0)
        try:
            # Comma is thousands (28,000); strip it
            s_no_comma = s.replace(",", "")
            # Dot: .000 = thousands (28.000), .50 = decimal
            if re.search(r"\.\d{3}(?:\d|$)", s_no_comma):
                s_clean = s_no_comma.replace(".", "")
                num = int(s_clean)
            elif "." in s_no_comma:
                num = float(s_no_comma)
            else:
                num = int(s_no_comma)
            return num2words(num, lang="es")
        except (ValueError, OverflowError):
            return m.group(0)

    # 10-11 digits (phone) → digit-by-digit
    text = re.sub(r"\b\d[\d\s\-]{9,14}\b", replace_phone, text)
    # Other numbers (prices, quantities, addresses)
    text = re.sub(r"\b\d{1,3}(?:[.,]\d{3})*(?:[.,]\d+)?\b|\b\d+\b", replace_number, text)
    return text


async def _normalize_text_stream(
    text_stream: AsyncIterable[str],
    log_fn=None,
) -> AsyncIterable[str]:
    """Buffer full text, normalize numbers (avoids splitting e.g. 28+000), then yield."""
    chunks = []
    async for chunk in text_stream:
        chunks.append(chunk)
    full_text = "".join(chunks)
    normalized = _normalize_numbers_for_tts(full_text)
    if log_fn:
        log_fn(full_text, normalized)
    if normalized:
        yield normalized


def _setup_braintrust_telemetry() -> None:
    """Configure Braintrust OpenTelemetry for tracing voice interactions and LLM calls.

    When BRAINTRUST_API_KEY is set, all LiveKit agent traces (STT, reasoning, tool calls,
    TTS) are sent to Braintrust for observability and evaluation.
    """
    if not os.environ.get("BRAINTRUST_API_KEY"):
        return
    try:
        from braintrust.otel import BraintrustSpanProcessor
        from opentelemetry.sdk.trace import TracerProvider

        project = os.environ.get("BRAINTRUST_PARENT", "project:restaurant-voice-agent")
        processor = BraintrustSpanProcessor(parent=project, filter_ai_spans=True)
        provider = TracerProvider()
        provider.add_span_processor(processor)
        set_tracer_provider(provider)
        print(f"Braintrust tracing enabled (project: {project})")
    except ImportError as e:
        print(f"Warning: Braintrust tracing skipped (install braintrust[otel]): {e}")
    except Exception as e:
        print(f"Warning: Braintrust tracing setup failed: {e}")


class CustomTurnDetector:
    """Wrapper around MultilingualModel that logs EOU probability for observability.
    Extend with: custom thresholds, rule blending, RPC to frontend, etc.
    """

    def __init__(self, obs_ctx: ObservabilityContext | None = None):
        self._model = MultilingualModel()
        self.last_eou_probability: float | None = None
        self.obs_ctx = obs_ctx

    @property
    def model(self) -> str:
        return self._model.model

    @property
    def provider(self) -> str:
        return self._model.provider

    async def unlikely_threshold(self, language: str | None) -> float | None:
        return await self._model.unlikely_threshold(language)

    async def supports_language(self, language: str | None) -> bool:
        return await self._model.supports_language(language)

    async def predict_end_of_turn(
        self, chat_ctx: llm.ChatContext, *, timeout: float | None = 3
    ) -> float:
        probability = await self._model.predict_end_of_turn(chat_ctx, timeout=timeout)
        # Rule blending: hesitation/filler — if last word is filler and prob < 0.7, wait longer
        last_user_text = self._last_user_text(chat_ctx)
        if last_user_text:
            probability = self._blend_hesitation(probability, last_user_text)
        self.last_eou_probability = probability
        # Log EOU for observability
        if self.obs_ctx:
            self.obs_ctx.log_event(
                "eou_probability", "turn_detection", eou_probability=round(probability, 4)
            )
        return probability

    def _last_user_text(self, chat_ctx: llm.ChatContext) -> str:
        """Extract last user message text from chat context."""
        text = ""
        for item in reversed(chat_ctx.items):
            if getattr(item, "type", None) == "message" and getattr(item, "role", None) == "user":
                text = (getattr(item, "text_content", None) or "")
                break
        return (text or "").strip().lower()

    # Filler/hesitation words (Spanish + universal); user likely still thinking
    _FILLER_WORDS = frozenset(
        {"eh", "este", "mmm", "um", "uh", "ehh", "pues", "em", "ah", "o", "sea"}
    )

    def _blend_hesitation(self, probability: float, text: str) -> float:
        """If last word is filler and prob < 0.7, reduce EOU to wait longer."""
        words = text.split()
        last_word = (words[-1] if words else "").strip(".,;:?!\"'")
        if last_word in self._FILLER_WORDS and probability < 0.7:
            # User might be hesitating; wait longer (blend down)
            return probability * 0.5
        return probability


class RestaurantAssistant(Agent):
    def __init__(self, obs_ctx: ObservabilityContext = None) -> None:
        super().__init__(
            instructions="""Tu nombre es Daniela y eres la asistente amigable de Biela, hamburguesería en la ciudad de Pasto, Colombia. Ayudas a los clientes a ordenar.

IMPORTANTE - Flujo de pedido:
1. Saluda: "Hola, ¿cómo estás? Bienvenido a Biela. Soy Daniela."
2. Pregunta: "¿Te gustaría ver el menú o ya sabes qué quieres ordenar?"
3. Si dice menú: ofrece categorías (get_categories con include_drinks=false): "Tenemos hamburguesas, perros calientes, papas fritas, hamburguesas de pollo, menú infantil, y carne y costillas. ¿Qué categoría te gustaría ver?"
4. Si ya sabe qué quiere: que diga el producto y búscalo en el menú
5. Cuando elija categoría: usa get_menu con esa categoría (mapea: hamburguesas→Burgers, perros calientes→Hot Dogs, papas fritas→Fries, hamburguesas de pollo→Chicken Burgers, menú infantil→Menú Infantil, carne y costillas→Steak & Ribs)
6. Repite para más platos principales si quiere
7. DESPUÉS del plato principal: "¿Te gustaría agregar alguna bebida?" → get_menu con category="Bebidas"
8. Pedido completo: pide nombre, apellido y teléfono
9. Pide dirección de entrega y barrio (district). Usa city="Pasto", state="Nariño", postalCode="150001"
10. Pide método de pago (efectivo o tarjeta). El pago es en el lugar, no pidas datos de tarjeta
11. Llama create_order con: first_name, last_name, phone, address, district, city, state, postal_code, payment_method, items_json. items_json es un JSON: [{"product_id": "...", "product_name": "Barracuda", "quantity": 1, "unit_price": 28000}]
12. Confirma el pedido creado y despide: "Tu pedido llegará en 30 minutos. ¡Gracias por ordenar en Biela!"

Herramientas:
- get_categories(include_drinks): Lista categorías. Usa false para platos principales, true después para incluir bebidas
- get_menu(category): Menú filtrado por categoría (Burgers, Hot Dogs, Fries, Chicken Burgers, Menú Infantil, Steak & Ribs, Bebidas)
- create_order(first_name, last_name, phone, address, district, city, state, postal_code, payment_method, items_json): Crea el pedido con todos los datos en una sola llamada

Al presentar el menú: usa lenguaje natural con conectores, como un mesero real. Di por ejemplo: "Tenemos la Barracuda que vale 28000 pesos y trae pan artesanal, carne, tocineta y papas fritas. También tenemos la Biela que vale 28000 y trae jamón, queso, tomate... También la Beta..." Usa: tenemos, también tenemos, que vale, y trae. No leas la lista tal cual. NO uses numeración (1., 2., 3.).

IMPORTANTE - Evita redundancia:
- Cuando el cliente elige un producto: confirma brevemente, por ejemplo "Perfecto, una Barracuda. ¿Algo más?" o "Listo, Barracuda. ¿Algo más?" NO repitas descripción ni precio.
- No pidas confirmación múltiple del pedido. Una vez que tengas nombre, dirección, pago e items: llama create_order y confirma una sola vez. NO preguntes "¿Confirmas tu pedido?" antes ni después de crear la orden.

Siempre pregunta primero: menú o producto específico. Si menú → categorías → get_menu por categoría. Si ya sabe → busca el producto. Bebidas solo después del plato principal."""
        )

        # Initialize thinking sounds
        self.thinking_sounds = {
            "thinking": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
            "processing": "https://www.soundjay.com/misc/sounds/clock-ticking-1.wav",
            "searching": "https://www.soundjay.com/misc/sounds/typewriter-1.wav"
        }
        self.current_sound = None
        self.obs_ctx = obs_ctx

    async def play_thinking_sound(self, sound_type: str = "thinking"):
        """Play a thinking sound during tool execution (only when room is available, e.g. not in console)."""
        room = getattr(self, "room", None)
        if not room or sound_type not in self.thinking_sounds:
            return
        sound_url = self.thinking_sounds[sound_type]
        try:
            await room.play_audio(sound_url, loop=True)
            self.current_sound = sound_url
        except Exception as e:
            print(f"Error playing thinking sound: {e}")

    async def stop_thinking_sound(self):
        """Stop the current thinking sound."""
        room = getattr(self, "room", None)
        if not room or not self.current_sound:
            self.current_sound = None
            return
        try:
            await room.stop_audio()
        except Exception as e:
            print(f"Error stopping thinking sound: {e}")
        finally:
            self.current_sound = None

    @function_tool()
    async def get_categories(self, include_drinks: bool = False) -> str:
        """Get the list of menu categories in Spanish. Use include_drinks=False for platos principales; True to include Bebidas after main dish is complete."""
        return get_categories(include_drinks=include_drinks)

    @function_tool()
    async def get_menu(self, category: str = None) -> str:
        """Get the restaurant menu, optionally filtered by category. Categories: Burgers, Hot Dogs, Fries, Chicken Burgers, Menú Infantil, Steak & Ribs, Bebidas."""
        tool_name = "get_menu"
        start_time = time.time()
        
        if self.obs_ctx:
            self.obs_ctx.log_tool_call_start(tool_name)
        
        await self.play_thinking_sound("searching")

        try:
            products = get_menu(category=category)
            if products:
                result = format_menu_for_voice(products)
            else:
                # Fallback: apologize and suggest next step
                result = "Lo siento, no puedo obtener el menú en este momento debido a un problema técnico. Por favor, inténtalo de nuevo en unos momentos o puedes decirme qué te gustaría ordenar directamente."
        except Exception as e:
            # Fallback on error
            result = "Lo siento, hubo un problema al obtener el menú. Por favor, inténtalo de nuevo más tarde o puedes decirme qué te gustaría ordenar."
            if self.obs_ctx:
                self.obs_ctx.log_event("tool_call_error", "tool_call", tool_name=tool_name, error=str(e))
        finally:
            # Stop thinking sound
            await self.stop_thinking_sound()
            
            if self.obs_ctx:
                latency_ms = (time.time() - start_time) * 1000
                self.obs_ctx.log_tool_call_end(tool_name, latency_ms)

        return result

    @function_tool()
    async def create_order(
        self,
        first_name: str,
        last_name: str,
        phone: str,
        address: str,
        city: str,
        postal_code: str,
        payment_method: str,
        items_json: str,
        district: str | None = None,
        state: str | None = None,
    ) -> str:
        """Create an order with customer data, delivery address, payment method and items.
        items_json: JSON array, e.g. [{"product_id": "...", "product_name": "Barracuda", "quantity": 1, "unit_price": 28000}]"""
        tool_name = "create_order"
        start_time = time.time()

        if self.obs_ctx:
            self.obs_ctx.log_tool_call_start(tool_name)

        await self.play_thinking_sound("processing")

        try:
            order_id = create_order(
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                address=address,
                district=district or None,
                city=city,
                state=state or None,
                postal_code=postal_code,
                payment_method=payment_method,
                items_json=items_json,
            )
            if order_id:
                result = f"¡Listo! He creado tu pedido correctamente. Tu orden está confirmada. Llegará en aproximadamente 30 minutos. ¡Gracias por ordenar en Biela!"
            else:
                result = "Lo siento, hubo un problema técnico al crear tu pedido. Por favor, verifica los datos e inténtalo de nuevo."
        except Exception as e:
            result = "Lo siento, hubo un error al procesar tu pedido. Por favor, inténtalo de nuevo en unos momentos."
            if self.obs_ctx:
                self.obs_ctx.log_event("tool_call_error", "tool_call", tool_name=tool_name, error=str(e))
        finally:
            await self.stop_thinking_sound()
            if self.obs_ctx:
                latency_ms = (time.time() - start_time) * 1000
                self.obs_ctx.log_tool_call_end(tool_name, latency_ms)

        return result

    async def on_user_turn_completed(
        self, turn_ctx: llm.ChatContext, new_message: llm.ChatMessage
    ) -> None:
        """Called when the user's turn has ended (final transcript). Log STT receive and record turn start for E2E timing."""
        transcript = (new_message.text_content or "").strip() if new_message else ""
        if self.obs_ctx:
            self.obs_ctx.set_turn_start_time(time.time())
            # transcript_delay not available from ChatMessage; set DEBUG=true to include transcript text
            self.obs_ctx.log_stt_receive(transcript=transcript or None, transcript_delay_s=None)

    async def tts_node(
        self, text: AsyncIterable[str], model_settings: ModelSettings
    ) -> AsyncIterable[rtc.AudioFrame]:
        """Wrap default TTS: normalize numbers for pronunciation, log turn E2E and TTS end."""
        tts_start = time.time()
        if self.obs_ctx:
            self.obs_ctx.log_turn_e2e_if_set(tts_start)

        def _log_tts(raw: str, normalized: str) -> None:
            if self.obs_ctx:
                self.obs_ctx.log_event(
                    "tts_input",
                    "tts",
                    raw_preview=raw[:400] if raw else "",
                    normalized_preview=normalized[:400] if normalized else "",
                )

        normalized_text = _normalize_text_stream(text, log_fn=_log_tts)
        async for frame in Agent.default.tts_node(self, normalized_text, model_settings):
            yield frame
        if self.obs_ctx:
            self.obs_ctx.log_tts_end((time.time() - tts_start) * 1000)


async def entrypoint(ctx: agents.JobContext):
    # Setup Braintrust tracing (optional; requires BRAINTRUST_API_KEY)
    _setup_braintrust_telemetry()

    # Start health check server
    health_port = int(os.getenv("HEALTH_CHECK_PORT", "8080"))
    try:
        start_health_server(port=health_port)
        print(f"Health check server started on port {health_port}")
    except Exception as e:
        print(f"Warning: Could not start health check server: {e}")
    
    # Initialize observability context
    # Use room/job id when present; in console mode ctx uses mocks → treat as missing and use UUID
    session_id = str(uuid.uuid4())
    try:
        candidate = None
        if hasattr(ctx, "room") and ctx.room and hasattr(ctx.room, "sid"):
            candidate = str(ctx.room.sid)
        elif hasattr(ctx, "job_id"):
            candidate = str(ctx.job_id)
        if candidate and "Mock" not in candidate and "mock" not in candidate:
            session_id = candidate
    except Exception:
        pass

    user_id = None  # Extract from room metadata if available
    obs_ctx = get_observability_context(session_id, user_id)
    
    # Log session start
    obs_ctx.log_event("session_start", "session")
    
    # Log STT provider configuration
    obs_ctx.log_stt_start()
    
    # Create TTS with error handling fallback
    # Run 7 / 7b / 7c: TTS — voice Marcela; model from ELEVEN_TTS_MODEL (default eleven_turbo_v2_5).
    # Try "eleven_multilingual_v2" (better quality) or "eleven_flash_v2_5" (faster, lower latency).
    # ELEVEN_API_KEY must be set (see https://docs.livekit.io/agents/models/tts/plugins/elevenlabs).
    tts_model = os.environ.get("ELEVEN_TTS_MODEL", "eleven_turbo_v2_5")
    try:
        tts = elevenlabs.TTS(
            model=tts_model,
            # voice_id="86V9x9hrQds83qf7zaGn",  # Marcela (Colombian); baseline premade is rola ODq5zmih8GrVes37Dizd
            voice_id="ODO4sbmD3pTjhgRVVRP6",
            language="es",
        )
    except Exception as e:
        print(f"Warning: TTS initialization failed: {e}. TTS will be disabled.")
        obs_ctx.log_event("tts_init_error", "tts", error=str(e))
        # Fallback: use a basic TTS or disable
        tts = None
    
    # Custom turn detector: wraps MultilingualModel, logs EOU for observability
    turn_detector = CustomTurnDetector(obs_ctx=obs_ctx)

    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=tts,
        vad=silero.VAD.load(),
        turn_detection=turn_detector,
    )

    # Create agent with observability context
    agent = RestaurantAssistant(obs_ctx=obs_ctx)
    
    # Wrap session start with timing and error handling
    try:
        # Create room input options with optional noise cancellation (LiveKit Cloud only)
        room_input_options_kwargs = {}
        
        # Try to use noise cancellation if available (LiveKit Cloud only)
        try:
            from livekit.plugins import noise_cancellation
            room_input_options_kwargs["noise_cancellation"] = noise_cancellation.BVC()
        except ImportError:
            # Noise cancellation not available (e.g., self-hosted deployments)
            # This is optional and can be omitted
            pass
        
        with obs_ctx.time_stage("session_start"):
            await session.start(
                room=ctx.room,
                agent=agent,
                room_input_options=RoomInputOptions(**room_input_options_kwargs),
            )
    except Exception as e:
        obs_ctx.log_event("session_start_error", "session", error=str(e))
        print(f"Error starting session: {e}")
        raise

    await ctx.connect()
    
    # Log reasoning start before generating reply
    obs_ctx.log_reasoning_start()
    reasoning_start = time.time()
    
    # Generate initial reply with timing and error handling
    try:
        with obs_ctx.time_stage("reasoning"):
            await session.generate_reply(
                instructions="Saluda: Hola, ¿cómo estás? Bienvenido a Biela, hamburguesería en Pasto. Soy Daniela. Pregunta: ¿Te gustaría ver el menú o ya sabes qué quieres ordenar?"
            )
        
        # Log reasoning end
        reasoning_latency = (time.time() - reasoning_start) * 1000
        obs_ctx.log_reasoning_end(reasoning_latency)
        
        # Log TTS start (TTS happens asynchronously after generate_reply)
        obs_ctx.log_tts_start()
    except Exception as e:
        obs_ctx.log_event("reasoning_error", "reasoning", error=str(e))
        print(f"Error generating reply: {e}")
        # Note: LiveKit will handle the error, but we log it for observability


if __name__ == "__main__":
    agents.cli.run_app(
        agents.WorkerOptions(
            entrypoint_fnc=entrypoint,
            agent_name="restaurant-agent",
        )
    )
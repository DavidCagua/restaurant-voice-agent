from dotenv import load_dotenv
import asyncio
import json
import os

from livekit import agents
from livekit.agents import AgentSession, Agent, RoomInputOptions, function_tool
from livekit.plugins import (
    openai,
    elevenlabs,
    deepgram,
    noise_cancellation,
    silero,
)
from livekit.plugins.turn_detector.multilingual import MultilingualModel

from restaurant_tools import (
    get_menu,
    create_customer_account,
    save_delivery_address,
    get_delivery_addresses,
    format_menu_for_voice
)

load_dotenv()


class RestaurantAssistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions="""Your name is Daniela and you are a friendly Spanish-speaking restaurant assistant for the restaurant La Pizzeria in Pasto, Colombia. Your job is to help customers order food.

Key responsibilities:
1. Greet customers warmly in Spanish start with "Hola, ¿cómo estás? Bienvenido a La Pizzeria" and introduce yourself as Daniela
2. Ask them if they would like to see the menu or order something specific
3. If they would like to see the menu, show them the menu
4. If they would like to order something specific, ask them for the item they would like to order
7. once they know what to order ask for their name, last name and phone number and save customer account, use the email [first_name]@example.com and password @Test123, keep the user id for later use in the save_delivery_address tool
9. After that ask for their delivery address,
10. After that ask for barrio which corresponds to district
11. save delivery address, name is "Casa", city is "Pasto", state is "Nariño", postal code is "150001", address2 is "", district is barrio, userId is the user id of the customer
12. Confirm order and ask for payment method, card or cash, THE PAYMENTS IS DUE IN PLACE SO NO NEED TO ASK FOR CARD DETAILS
13. Once confirmed, tell them that order will be delivered in 30 minutes and ask them if they have any other questions
14. thank them for their order and say goodbye

Always be polite and helpful. If a customer seems confused, guide them through the process step by step.

You have access to these tools:
- get_menu: Get the current restaurant menu
- create_customer_account: Create a new customer account
- save_delivery_address: Save a delivery address
- get_delivery_addresses: Get saved delivery addresses

Use these tools when appropriate to help customers. When customers want to order multiple items, use calculate_order_total to show them the breakdown and total."""
        )

        # Initialize thinking sounds
        self.thinking_sounds = {
            "thinking": "https://www.soundjay.com/misc/sounds/bell-ringing-05.wav",
            "processing": "https://www.soundjay.com/misc/sounds/clock-ticking-1.wav",
            "searching": "https://www.soundjay.com/misc/sounds/typewriter-1.wav"
        }
        self.current_sound = None

    async def play_thinking_sound(self, sound_type: str = "thinking"):
        """Play a thinking sound during tool execution"""
        if sound_type in self.thinking_sounds:
            sound_url = self.thinking_sounds[sound_type]
            try:
                # Play the thinking sound using the room's audio player
                await self.room.play_audio(sound_url, loop=True)
                self.current_sound = sound_url
            except Exception as e:
                print(f"Error playing thinking sound: {e}")

    async def stop_thinking_sound(self):
        """Stop the current thinking sound"""
        if self.current_sound:
            try:
                await self.room.stop_audio()
                self.current_sound = None
            except Exception as e:
                print(f"Error stopping thinking sound: {e}")

    @function_tool()
    async def get_menu(self) -> str:
        """Get the current restaurant menu with prices and descriptions"""
        # Start thinking sound
        await self.play_thinking_sound("searching")

        try:
            products = get_menu()
            if products:
                result = format_menu_for_voice(products)
            else:
                result = "Lo siento, no puedo obtener el menú en este momento. Por favor, inténtalo de nuevo más tarde."
        finally:
            # Stop thinking sound
            await self.stop_thinking_sound()

        return result

    @function_tool()
    async def create_customer_account(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        phone: str
    ) -> str:
        """Create a new customer account with name, email, password, and phone"""
        # Start thinking sound
        await self.play_thinking_sound("processing")

        try:
            success = create_customer_account(
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                phone=phone
            )
            if success:
                result = f"¡Perfecto! He creado tu cuenta, {first_name}. Ahora puedes hacer tu pedido."
            else:
                result = "Lo siento, hubo un problema al crear tu cuenta. Por favor, verifica tus datos e inténtalo de nuevo."
        finally:
            # Stop thinking sound
            await self.stop_thinking_sound()

        return result

    @function_tool()
    async def save_delivery_address(
        self,
        name: str,
        address: str,
        city: str,
        state: str,
        postal_code: str,
        district: str = None,
        userId: str = None
    ) -> str:
        """Save a delivery address for the customer"""
        # Start thinking sound
        await self.play_thinking_sound("processing")

        try:
            success = save_delivery_address(
                name="Casa",
                address=address,
                city="Pasto",
                state="Nariño",
                postal_code="150001",
                district=district,
                userId=userId
            )
            if success:
                result = f"¡Excelente! He guardado tu dirección de entrega: {address}."
            else:
                result = "Lo siento, hubo un problema al guardar tu dirección. Por favor, verifica los datos e inténtalo de nuevo."
        finally:
            # Stop thinking sound
            await self.stop_thinking_sound()

        return result

    @function_tool()
    async def get_delivery_addresses(self) -> str:
        """Get saved delivery addresses for the customer"""
        # Start thinking sound
        await self.play_thinking_sound("searching")

        try:
            addresses = get_delivery_addresses()
            if addresses:
                address_list = "\n".join([f"- {addr.name}: {addr.address}, {addr.city}" for addr in addresses])
                result = f"Tus direcciones guardadas son:\n{address_list}"
            else:
                result = "No tienes direcciones guardadas. ¿Te gustaría agregar una nueva?"
        finally:
            # Stop thinking sound
            await self.stop_thinking_sound()

        return result


async def entrypoint(ctx: agents.JobContext):
    session = AgentSession(
        stt=deepgram.STT(model="nova-3", language="multi"),
        llm=openai.LLM(model="gpt-4o-mini"),
        tts=elevenlabs.TTS(model="eleven_multilingual_v2", voice_id="86V9x9hrQds83qf7zaGn"), #rola
        # tts=elevenlabs.TTS(model="eleven_multilingual_v2", voice_id="J4vZAFDEcpenkMp3f3R9"), #paisa
        vad=silero.VAD.load(),
        turn_detection=MultilingualModel(),
    )

    await session.start(
        room=ctx.room,
        agent=RestaurantAssistant(),
        room_input_options=RoomInputOptions(
            # LiveKit Cloud enhanced noise cancellation
            # - If self-hosting, omit this parameter
            # - For telephony applications, use `BVCTelephony` for best results
            noise_cancellation=noise_cancellation.BVC(),
        ),
    )

    await ctx.connect()

    await session.generate_reply(
        instructions="Saluda al cliente de manera cálida y amigable. Pregúntale si le gustaría ver el menú o si necesita ayuda con algo más."
    )


if __name__ == "__main__":
    agents.cli.run_app(agents.WorkerOptions(entrypoint_fnc=entrypoint))
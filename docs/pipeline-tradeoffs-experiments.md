# Pipeline and tradeoffs — experiments log

Track what we do for this part of prep and record latency + data values.

**Fixed script:** Agent greets → I ask for the menu (e.g. "El menú, por favor") → same interaction every run.

**Rule:** Change one variable per run. Note config + results below.

---

## Baseline (default config)

| Field | Value |
|-------|--------|
| Date / run | 2026-02-24 |
| STT | deepgram nova-3, language=multi |
| LLM | gpt-4o-mini |
| TTS | elevenlabs eleven_turbo_v2_5, voice rola, language=es |
| VAD / turn detection | silero VAD, MultilingualModel |
| **Latency** | |
| Session start (ms) | 30.35 |
| First-turn reasoning (ms) | 10737.82 |
| turn_e2e (ms) | 5.84 |
| Tool call get_menu (ms) | 84.65 |
| tts_end greeting (ms) | 1986.92 |
| tts_end menu reply 1st chunk (ms) | 1607.77 |
| tts_end menu reply 2nd chunk (ms) | 3833.51 |
| User transcript (what STT heard) | El menú, por favor. |
| transcript_delay (s) | 0.23 |
| Notes | DEBUG=true. Same script: greet → "El menú, por favor." |

---

## Run 2: STT Nova-3 → Nova-2

| Field | Value |
|-------|--------|
| Date / run | 2026-02-24 |
| **What we changed** | STT: nova-3 → nova-2 (language=multi same) |
| STT | deepgram nova-2, language=multi |
| LLM | gpt-4o-mini (unchanged) |
| TTS | elevenlabs eleven_turbo_v2_5 (unchanged) |
| **Latency** | |
| Session start (ms) | 23.81 |
| First-turn reasoning (ms) | 12436.15 |
| turn_e2e (ms) | 5.09 |
| Tool call get_menu (ms) | 87.49 |
| tts_end greeting (ms) | 2382.58 |
| tts_end menu reply 1st (ms) | 1554.33 |
| tts_end menu reply 2nd (ms) | 2635.42 |
| User transcript | El menú por favor |
| transcript_delay (s) | 0.62 |
| Notes / comparison to baseline | Same script. Nova-2: reasoning ~1.7s higher, transcript_delay ~2.7× higher (0.62 vs 0.23). Transcript OK (no comma). Session start similar. |

---

## Run 3: STT Nova-3 language multi → es

| Field | Value |
|-------|--------|
| Date / run | 2026-02-24 |
| **What we changed** | STT: nova-3 language=multi → language=es (model same) |
| STT | deepgram nova-3, language=es |
| LLM | gpt-4o-mini (unchanged) |
| TTS | elevenlabs eleven_turbo_v2_5 (unchanged) |
| **Latency** | |
| Session start (ms) | 25.83 |
| First-turn reasoning (ms) | 10136.41 |
| turn_e2e (ms) | 5.37 |
| Tool call get_menu (ms) | 78.37 |
| tts_end greeting (ms) | 1690.38 |
| tts_end menu reply 1st (ms) | 1274.99 |
| tts_end menu reply 2nd (ms) | 2991.03 |
| User transcript | El menú, por favor. |
| transcript_delay (s) | 0.69 |
| Notes / comparison | Same script. Nova-3+es: reasoning ~600ms lower than baseline (multi). Transcript exact (with comma). transcript_delay higher this run (0.69). |

---

## Run 4: STT Flux (English script)

| Field | Value |
|-------|--------|
| Date / run | 2026-02-24 |
| **What we changed** | STT: Flux (flux-general-en). Script in English (not comparable to baseline phrase). |
| STT | deepgram STTv2 flux-general-en (English-only) |
| LLM | gpt-4o-mini (unchanged) |
| TTS | elevenlabs eleven_turbo_v2_5 (unchanged) |
| **Latency** | |
| Session start (ms) | 28.39 |
| First-turn reasoning (ms) | 12039.96 |
| turn_e2e (ms) | 5.14 |
| Tool call get_menu (ms) | 91.91 |
| tts_end greeting (ms) | 2183.89 |
| tts_end menu reply 1st (ms) | 1128.52 |
| tts_end menu reply 2nd (ms) | 2642.26 |
| User transcript | The menu, please. |
| transcript_delay (s) | 0.53 |
| Notes / comparison | Flux run. User said "The menu, please" (English). Transcript exact. Not directly comparable to baseline (different phrase); use for Flux streaming/low-latency reference. |

---

## Run 5: LLM gpt-4o-mini → gpt-4o

**Rule:** Change only LLM (keep STT = Nova-3 multi, TTS = elevenlabs). Same script: "El menú, por favor."

| Field | Value |
|-------|--------|
| Date / run | 2026-02-24 |
| **What we changed** | LLM: gpt-4o-mini → gpt-4o |
| STT | nova-3 multi (unchanged) |
| LLM | openai gpt-4o |
| TTS | elevenlabs (unchanged) |
| **Latency** | |
| Session start (ms) | 23.05 |
| First-turn reasoning (ms) | 9630.63 |
| turn_e2e (ms) | 5.46 |
| Tool call get_menu (ms) | 82.11 |
| tts_end greeting (ms) | 1934.64 |
| tts_end menu reply 1st (ms) | 2071.46 |
| tts_end menu reply 2nd (ms) | 3236.76 |
| User transcript | El menú, por favor. |
| Notes / comparison to baseline | gpt-4o: reasoning ~1.1s lower than baseline (9630 vs 10737). Transcript same. (Logs still show model "gpt-4o-mini" from observability default; actual LLM was gpt-4o.) |

---

## Run 6: LLM gpt-3.5-turbo

**Rule:** Change only LLM. Same script: "El menú, por favor."

| Field | Value |
|-------|--------|
| Date / run | 2026-02-24 |
| **What we changed** | LLM: gpt-3.5-turbo (older OpenAI model) |
| STT | nova-3 multi (unchanged) |
| LLM | openai gpt-3.5-turbo |
| TTS | elevenlabs (unchanged) |
| **Latency** | |
| Session start (ms) | 24.29 |
| First-turn reasoning (ms) | 17239.73 |
| turn_e2e (ms) | 5.1 |
| Tool call get_menu (ms) | 82.46 |
| tts_end (greeting; 3.5 called get_menu in 1st turn) | 5583.71, 3457.97 |
| tts_end menu reply (ms) | 4706.1 |
| User transcript | El menú, por favor. |
| transcript_delay (s) | 0.40 |
| Notes / comparison to baseline | gpt-3.5-turbo: first-turn reasoning much higher (17239 vs 10737) — model called get_menu during greeting turn. Transcript same. Quality of attention degraded: LLM added unnecessary kind/filler sentences to the script. |

---

## Run 7: TTS — Colombian voice (Marcela)

**Rule:** Change only TTS (keep STT = Nova-3 multi, LLM = gpt-4o-mini). Same script: "El menú, por favor."

**Note:** Voice `86V9x9hrQds83qf7zaGn` (Marcela – Spanish Colombian, Voice Library) requires a **paid** ElevenLabs plan; on free tier the API returns 402 "Free users cannot use library voices via the API." With a paid plan the same voice works.

| Field | Value |
|-------|--------|
| Date / run | 2026-02-24 |
| **What we changed** | TTS voice → Marcela (86V9x9hrQds83qf7zaGn), eleven_turbo_v2_5, language=es |
| STT | nova-3 multi (unchanged) |
| LLM | gpt-4o-mini (unchanged) |
| TTS | elevenlabs eleven_turbo_v2_5, voice Marcela (Colombian), language=es |
| **Latency** | |
| Session start (ms) | 21.83 |
| First-turn reasoning (ms) | 9635.71 |
| turn_e2e (ms) | 5.1 |
| Tool call get_menu (ms) | 85.84 |
| tts_end greeting (ms) | 2390.7 |
| tts_end menu reply 1st (ms) | 1320.45 |
| tts_end menu reply 2nd (ms) | 3047.55 |
| User transcript | El menú, por favor. |
| transcript_delay (s) | 0.40 |
| Notes / comparison to baseline | Colombian voice (Marcela) run. Greeting TTS ~400 ms slower than baseline (2390 vs 1986); first chunk faster (1320 vs 1607), second chunk faster (3047 vs 3833). Reasoning in line with Run 5 (gpt-4o). "flush audio emitter due to slow audio generation" once. |

---

## Run 7b: TTS model → eleven_multilingual_v2 (better quality)

**Rule:** Change only TTS model (keep voice Marcela, STT = Nova-3 multi, LLM = gpt-4o-mini). Same script: "El menú, por favor."

**Run with:** `ELEVEN_TTS_MODEL=eleven_multilingual_v2 DEBUG=true python agent.py console`

**Note:** Multilingual v2 is ElevenLabs’ “most lifelike” production model; higher latency and cost than Turbo v2.5. Expect slower first-byte / tts_end vs Run 7.

| Field | Value |
|-------|--------|
| Date / run | 2026-02-24 |
| **What we changed** | TTS model: eleven_turbo_v2_5 → eleven_multilingual_v2 |
| STT | nova-3 multi (unchanged) |
| LLM | gpt-4o-mini (unchanged) |
| TTS | elevenlabs eleven_multilingual_v2, voice Marcela, language=es |
| **Latency** | |
| Session start (ms) | 23.81 |
| First-turn reasoning (ms) | 10835.99 |
| turn_e2e (ms) | 5.49 |
| Tool call get_menu (ms) | 80.9 |
| tts_end greeting (ms) | 2145.18 |
| tts_end menu reply 1st (ms) | 1032.9 |
| tts_end menu reply 2nd (ms) | 3060.71 |
| User transcript | El menú, por favor. |
| transcript_delay (s) | 0.39 |
| Notes / comparison to Run 7 | Multilingual v2: greeting TTS ~245 ms faster than Run 7 (2145 vs 2390), first chunk ~290 ms faster (1032 vs 1320), second chunk similar (3060 vs 3047). Reasoning ~1.2 s higher (10835 vs 9635). One "resumed false interrupted speech" (timeout 2.0). |

---

## Run 7c: TTS model → eleven_flash_v2_5 (faster / lower latency)

**Rule:** Change only TTS model (keep voice Marcela, STT = Nova-3 multi, LLM = gpt-4o-mini). Same script: "El menú, por favor."

**Run with:** `ELEVEN_TTS_MODEL=eleven_flash_v2_5 DEBUG=true python agent.py console`

**Note:** Flash v2.5 is optimized for ultra-low latency (~75 ms); quality may be lower than Turbo v2.5. Expect lower tts_end latencies.

| Field | Value |
|-------|--------|
| Date / run | 2026-02-24 |
| **What we changed** | TTS model: eleven_turbo_v2_5 → eleven_flash_v2_5 |
| STT | nova-3 multi (unchanged) |
| LLM | gpt-4o-mini (unchanged) |
| TTS | elevenlabs eleven_flash_v2_5, voice Marcela, language=es |
| **Latency** | |
| Session start (ms) | 27.7 |
| First-turn reasoning (ms) | 11635.04 |
| turn_e2e (ms) | 5.27 |
| Tool call get_menu (ms) | 74.7 |
| tts_end greeting (ms) | 2463.65 |
| tts_end menu reply 1st (ms) | 1387.28 |
| tts_end menu reply 2nd (ms) | 2335.9 |
| User transcript | El menú, por favor. |
| transcript_delay (s) | 0.25 |
| Notes / comparison to Run 7 | Flash v2.5: greeting similar to Run 7 (2463 vs 2390); first chunk similar (1387 vs 1320); second chunk ~700 ms faster (2335 vs 3047). Reasoning highest of 7/7b/7c (11635 ms). transcript_delay lowest (0.25 s). |

---

## Run 8 (optional — stress): ____________________

Same config as baseline, but e.g. said "menu" fast/mumbly or with background noise.

| Field | Value |
|-------|--------|
| Date / run | |
| **What we changed** | (delivery / noise) |
| STT | |
| LLM | |
| TTS | |
| **Latency** | |
| User transcript | |
| Notes (where did it break?) | |

---

## Summary table (copy once you have a few runs)

| Run | What changed | Session start (ms) | Reasoning (ms) | Tool (ms) | Transcript OK? |
|-----|--------------|--------------------|---------------|-----------|----------------|
| Baseline | — | 30.35 | 10737.82 | 84.65 | Yes (El menú, por favor.) |
| 2 | STT nova-3→nova-2 | 23.81 | 12436.15 | 87.49 | Yes (El menú por favor) |
| 3 | STT nova-3 multi→es | 25.83 | 10136.41 | 78.37 | Yes (El menú, por favor.) |
| 4 | STT Flux, script EN | 28.39 | 12039.96 | 91.91 | Yes (The menu, please.) |
| 5 | LLM gpt-4o-mini→gpt-4o | 23.05 | 9630.63 | 82.11 | Yes (El menú, por favor.) |
| 6 | LLM gpt-3.5-turbo | 24.29 | 17239.73 | 82.46 | Yes (El menú, por favor.) |
| 7 | TTS voice → Marcela (Colombian) | 21.83 | 9635.71 | 85.84 | Yes (El menú, por favor.) |
| 7b | TTS model → eleven_multilingual_v2 | 23.81 | 10835.99 | 80.9 | Yes (El menú, por favor.) |
| 7c | TTS model → eleven_flash_v2_5 | 27.7 | 11635.04 | 74.7 | Yes (El menú, por favor.) |

---

## Tradeoff one-liners (fill after experiments)

- STT: When I switched to Nova-2 (multi), first-turn reasoning and transcript_delay went up vs Nova-3; when I switched to Nova-3 with language=es (vs multi), reasoning was slightly lower and transcript was the same. Flux (EN): transcript perfect for "The menu, please"; use for English streaming reference.
- LLM: When I switched to gpt-4o (from gpt-4o-mini), first-turn reasoning was ~1.1s lower this run (9630 vs 10737 ms baseline). When I switched to gpt-3.5-turbo, first-turn reasoning was much higher (17239 ms), the model called get_menu during the greeting turn, and quality of attention degraded (LLM added unnecessary kind/filler sentences to the script).
- TTS: When I switched to the Colombian Voice Library voice (Marcela), greeting TTS was ~400 ms slower than baseline (2390 vs 1986 ms); menu reply chunks were faster (1320 / 3047 vs 1607 / 3833 ms). Voice Library voices require a paid ElevenLabs plan for API use. Run 7b (eleven_multilingual_v2): greeting and first chunk faster than Run 7 (2145 / 1032 vs 2390 / 1320 ms); reasoning ~1.2 s higher. Run 7c (eleven_flash_v2_5): second chunk ~700 ms faster (2335 vs 3047 ms); reasoning highest (11635 ms); transcript_delay lowest (0.25 s).

---

## Analysis for interview prep (Section 1: Pipeline and tradeoffs)

*Use this with `docs/interview-prep-real-time-voice-ai.md` §1. All numbers from the runs above.*

### Pipeline sketch (what to say / draw)

```
[User speaks] → STT (Deepgram) → transcript
                    ↓
              LLM (OpenAI) ← tools (e.g. get_menu)
                    ↓
              TTS (ElevenLabs) → [audio to user]
```

- **STT:** Converts speech to text; latency shows up as *transcript_delay* (time until final transcript). Our baseline: ~0.23 s; Nova-2 gave ~0.62 s; Flash run gave 0.25 s.
- **LLM:** Takes transcript + context, may call tools; latency = *first-turn reasoning* (time until model finishes thinking / starts replying). Baseline ~10.7 s; gpt-4o ~9.6 s; gpt-3.5-turbo ~17.2 s.
- **TTS:** Converts reply text to audio; latency = *tts_end* per chunk (time to produce each chunk). Baseline greeting ~2 s, menu reply chunks ~1.6 s + ~3.8 s.
- **Cost:** Heavier STT/LLM/TTS = more $ per request; cheaper models (e.g. gpt-3.5, turbo TTS) trade quality or consistency.

### Where latency lives (with our numbers)

| Stage | What we measured | Typical range in our runs |
|-------|------------------|---------------------------|
| **Session start** | Time to first agent output | ~22–30 ms (small) |
| **STT** | transcript_delay (speech → final transcript) | 0.23–0.69 s (model/language dependent) |
| **LLM** | First-turn reasoning (thinking time) | 9.6–17.2 s (biggest lever: model choice) |
| **Tool** | get_menu call | ~75–92 ms (negligible) |
| **TTS** | tts_end per chunk (text → audio) | ~1–3.8 s per chunk (model/voice dependent) |
| **turn_e2e** | User stop speaking → we start TTS | ~5 ms (turn detection + pipeline handoff) |

- **Time to first word:** Dominated by session start + first reasoning + first TTS chunk. Improving “first word” = faster LLM (e.g. gpt-4o vs gpt-4o-mini), faster TTS first chunk, and/or streaming (start TTS on first tokens).
- **Time to complete reply:** Sum of reasoning + all TTS chunks (+ tool if any). LLM reasoning is the main driver (10–17 s in our runs).

### Tradeoffs I can explain (with data)

1. **STT accuracy vs latency:** Nova-2 (multi) gave ~1.7 s more reasoning and ~2.7× higher transcript_delay (0.62 vs 0.23 s) than Nova-3; transcript was still OK. So: “We could use a heavier STT for edge-case accuracy, but we saw latency and delay go up; we’d only do that if we had real accuracy issues.”
2. **LLM cost/quality vs latency:** gpt-4o cut reasoning by ~1.1 s vs gpt-4o-mini; gpt-3.5-turbo added ~6.5 s and hurt quality (wrong turn behavior, filler). So: “We could use a cheaper/smaller LLM but we measured much higher latency and worse quality; for voice we optimized for responsiveness and consistency.”
3. **TTS quality vs latency:** Multilingual v2 (premium) was *faster* on greeting/first chunk in our run than turbo; Flash v2.5 gave the fastest second chunk (~700 ms gain) but reasoning varied run-to-run. So: “TTS model choice affects both quality and chunk latency; we measured per-chunk tts_end and picked the balance that felt right for our use case.”

### Likely questions — short answers

- **“How would you design a voice AI system?”**  
  “As a pipeline: STT → LLM → TTS, with tools for the LLM. I’d instrument each stage—we logged session start, STT transcript_delay, LLM reasoning time, tool duration, and TTS chunk latency—so we could see where time and cost go. Then we change one variable at a time and measure; that’s how we chose models and providers.”

- **“How would you improve latency?”**  
  “First, measure. In our runs the biggest lever was the LLM: switching to a faster model (e.g. gpt-4o) cut first-turn reasoning by about a second; a slower one (gpt-3.5-turbo) added several seconds and hurt quality. Second, STT: a faster or more targeted model (e.g. Nova-3, or language=es) reduced transcript_delay. Third, TTS: we compared turbo, multilingual, and Flash and saw real differences in chunk latency; for real-time we’d pick the model that gives acceptable quality with the lowest tts_end. Streaming everywhere—STT, LLM, TTS—so we don’t wait for full sentences before starting the next stage.”

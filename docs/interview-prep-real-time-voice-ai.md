# Interview Prep: Real-Time Voice AI

**Interview date:** _______________  
**Role focus:** Senior Fullstack + AI / Real-time conversation

---

## 1. Pipeline and tradeoffs (highest leverage)

### Core idea
- **STT → LLM → TTS:** Draw it. Say what each step does and where **latency** and **cost** live.
- **Latency:** “Time to first word” vs “time to complete reply”; what affects each (streaming STT, streaming LLM, streaming TTS, network).
- **Tradeoffs:** “We could use a heavier STT for accuracy but latency goes up”; “we could use a cheaper LLM but quality drops.”
- **One-sentence answer:** “Real-time voice is a pipeline; you optimize by measuring each stage and making conscious tradeoffs.”

### My notes / rehearsal
<!-- Use this space to sketch the pipeline and write your own phrasing. Full analysis with numbers: see docs/pipeline-tradeoffs-experiments.md § "Analysis for interview prep". -->

- Pipeline sketch:
  - STT → LLM (+ tools) → TTS. Draw it; say latency and cost live at each stage. (Details + numbers in pipeline-tradeoffs-experiments.md.)
- Where latency lives:
  - Session start ~25 ms; STT transcript_delay 0.23–0.69 s; LLM reasoning 9.6–17.2 s (biggest); tool ~80 ms; TTS chunk 1–3.8 s per chunk.
- One tradeoff I can explain:
  - “Heavier STT (Nova-2) → higher transcript_delay; cheaper LLM (gpt-3.5) → +6 s reasoning and worse quality; TTS model choice trades quality vs chunk latency.”

### Likely questions
- “How would you design a voice AI system?”
- “How would you improve latency?”

---

## 2. Concrete experience with your project

### Restaurant voice agent
- **What it does:** (e.g. take orders, answer menu, …)
  - 
- **Stack:** (LiveKit, STT/LLM/TTS, …)
  - 
- **What I built:** (tools, API, …)
  - 

### One technical decision I made and why
- Decision:
- Why:
- 

### One problem I hit and how I fixed it
- Problem:
- Fix:
- 

### Story versions
- **2-minute version:** (Situation → Task → Action → Result)
  - 
- **5-minute version:**
  - 

---

## 3. Scalability and multi-tenant (senior angle)

**Scope:** We focus on **complex customization**—custom logic in turn detection, transcript processing, interruption handling—not just plug/unplug models.

### Key points
- **Per-tenant config:** Different clients need different languages, models, or compliance → drive config from **metadata** (job/room/participant), not hardcoding.
- **Customizing a pipeline:** Two levels—**simple** (plug/unplug models per tenant) and **complex** (custom logic: turn detector wrapper, stt_node override, manual turn control, STT endpointing). **We focus on complex.**
- **One-sentence answer:** “At scale you need per-tenant configuration and pluggable pipeline stages, not one global config.”

### My notes
- Full plan: **`docs/scalability-multi-tenant.md`** | Hands-on complex STT: **`docs/hands-on-turn-detection-interruptions.md`**
- How I’d support many clients:
  - Drive config from room/job metadata (language, STT/LLM/TTS model, voice); entrypoint builds the right pipeline per session; one codebase, env only for defaults and API keys.
- How I’d make the system more flexible (complex focus):
  - **Complex (primary):** Override nodes—custom turn detector wrapper (EOU observability, rule blending), stt_node (transcript post-processing, keyword detection, filler removal), custom EOU model, manual turn control, or STT endpointing. Real logic, not just args.
  - **Simple (supporting):** Config layer selects/swap STT/LLM/TTS per tenant from metadata. 

### Likely questions
- “How would you support many clients?”
- “How would you make the system more flexible?”

---

## 4. Failure modes and production

### What can go wrong
- Network drops
- STT/LLM timeouts
- Empty or partial transcripts
- User talking over the agent

### What I’d do
- Timeouts, retries, fallback messages, reconnection behavior
- Observability: logs, metrics, tracing

**One-sentence answer:** “In production you need clear failure handling and observability so you can detect and fix issues.”

### My notes
- One production issue (real or hypothetical):
  - 
- How I’d handle it:
  - 

### Likely questions
- “How do you make this production-ready?”
- “How do you debug a bad call?”

---

## 5. If they go deep on STT

**Scope:** We focus on **complex customization**—turn detection, transcript processing, interruption handling—not just parameter tweaks.

### Concepts to mention
- **Streaming vs non-streaming STT;** when you need **VAD + buffering** (e.g. Whisper).
- **Simple customization:** Pre-processing (audio), post-processing (text), provider/model selection, custom vocabulary; per-session config from metadata.
- **Complex customization (our focus):** Turn detection (VAD, EOU model, STT endpointing, manual), interruption handling, custom logic in pipeline nodes (turn detector wrapper, stt_node override, custom EOU model).

### Deep STT scope—complex customization (logic, not args)
| Path | What it adds |
|------|--------------|
| Custom turn detector wrapper | Wrap MultilingualModel; add EOU logging, RPC, custom thresholds, rule blending |
| Override `stt_node` | Post-process SpeechEvents (transcript, start/end of speech); keyword detection, filler removal, PII |
| Custom EOU model | Implement `predict_end_of_turn(chat_ctx) -> float`; rule-based or heuristic |
| Manual turn control | `turn_detection="manual"`; `commit_user_turn()`, `clear_user_turn()`, `interrupt()` |
| STT endpointing | `turn_detection="stt"`; use provider’s phrase endpointing (AssemblyAI, Deepgram Flux) |

### My notes
- See **`docs/hands-on-turn-detection-interruptions.md`** (hands-on) and **`docs/scalability-multi-tenant.md`** § Phase 4 (complex customization plan). 

---

## 6. Behavioral / senior

### Stories to prepare (STAR: Situation, Task, Action, Result)

| Theme           | Situation | Task | Action | Result |
|-----------------|-----------|------|--------|--------|
| **Ownership**   |           |      |        |        |
| **Tradeoffs**   |           |      |        |        |
| **Collaboration** |         |      |        |        |

---

## 7. Pre-interview checklist

**If you have 2 hours:** Focus on **§1 (pipeline)** + **§2 (your project)**.

- [ ] Draw STT→LLM→TTS once; rehearse “where is latency/cost” and one tradeoff.
- [ ] Write and rehearse 2‑min and 5‑min versions of the restaurant agent + one decision + one problem solved.
- [ ] Rehearse “how would you support many clients?” with metadata + configurable pipeline. Emphasize **complex customization** (turn detector wrapper, stt_node override, custom EOU).
- [ ] Think of one production issue (real or hypothetical) and how you’d handle it.
- [ ] Prepare one STAR story for ownership and one for tradeoffs.

---

## Quick reference: one-liners

| Topic              | One-liner |
|--------------------|-----------|
| Pipeline           | Real-time voice is a pipeline; you optimize by measuring each stage and making conscious tradeoffs. |
| Multi-tenant       | At scale you need per-tenant configuration and pluggable pipeline stages; we focus on complex customization (turn detector, stt_node, custom EOU). |
| Production        | In production you need clear failure handling and observability so you can detect and fix issues. |

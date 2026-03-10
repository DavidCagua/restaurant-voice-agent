# Hands-on: Turn detection and interruptions

**Goal:** Get hands-on with the complex STT layer—VAD, EOU, turn detection, and interruption handling—using your current restaurant voice agent.

**Scope:** We focus on **complex customization**—custom logic, not just parameter tweaks. Parameter experiments (e.g. min_silence_duration) are a baseline; deeper paths (custom turn detector wrapper, stt_node override, custom EOU model) are in `docs/scalability-multi-tenant.md` § Phase 4.

---

## What you already have

| Component | Your config | Role |
|-----------|-------------|------|
| **VAD** | `silero.VAD.load()` (defaults) | Detects speech vs silence; feeds turn detection |
| **Turn detection** | `MultilingualModel()` | Context-aware EOU (end-of-utterance); uses STT + LLM history |
| **Interruptions** | Default (enabled) | Agent stops when user speaks; false-interruption handling on |

---

## Experiments you can run (no new deps)

### 1. VAD-only vs MultilingualModel

**Idea:** Compare pure VAD turn detection (no language model) vs your current context-aware EOU.

**Change:** In `AgentSession`, switch:

```python
# Current (context-aware EOU)
turn_detection=MultilingualModel(),

# Experiment: VAD only (simpler, no EOU model)
turn_detection="vad",
```

**What to notice:** VAD-only tends to cut off users who pause mid-sentence; MultilingualModel waits when context suggests they have more to say. Try saying "El menú... por favor" with a long pause between—VAD-only may treat it as two turns.

---

### 2. VAD: `min_silence_duration`

**Idea:** How long silence before we decide the user finished speaking.

- **Lower (e.g. 0.3 s):** Faster response, but may cut off slow speakers.
- **Higher (e.g. 0.8 s):** Waits longer, fewer false ends, slower feel.

**Change:** In `silero.VAD.load()`:

```python
vad=silero.VAD.load(min_silence_duration=0.3),   # faster, more cuts
# or
vad=silero.VAD.load(min_silence_duration=0.8),   # slower, more patient
```

**Default:** 0.55 s.

---

### 3. VAD: `activation_threshold`

**Idea:** Sensitivity to speech vs noise.

- **Higher (e.g. 0.7):** More conservative; might miss soft speech.
- **Lower (e.g. 0.3):** More sensitive; might treat noise as speech.

**Change:**

```python
vad=silero.VAD.load(activation_threshold=0.7),  # noisy room
# or
vad=silero.VAD.load(activation_threshold=0.3),  # quiet, soft speech
```

**Default:** 0.5.

---

### 4. Interruption: `min_interruption_duration`

**Idea:** How long the user must speak before we treat it as an interruption (and stop the agent).

- **Lower (e.g. 0.3 s):** Interrupts faster; more reactive, more false interrupts.
- **Higher (e.g. 0.8 s):** Waits longer; fewer false interrupts, feels less responsive.

**Change:** In `AgentSession`:

```python
session = AgentSession(
    # ...
    min_interruption_duration=0.3,  # more eager to interrupt
    # or
    min_interruption_duration=0.8,  # more patient
)
```

**Default:** 0.5 s.

---

### 5. False interruption: `false_interruption_timeout` and `resume_false_interruption`

**Idea:** You saw "resumed false interrupted speech" in Run 7b. That’s the system treating noise or a brief sound as user speech, stopping the agent, then resuming when no real transcript appears.

- **`false_interruption_timeout`:** Seconds to wait before deciding it was a false alarm and resuming. Default 2.0.
- **`resume_false_interruption`:** Whether to resume. Default True.

**Change:**

```python
session = AgentSession(
    # ...
    false_interruption_timeout=1.0,   # faster resume (might cut off real interrupts)
    resume_false_interruption=True,   # keep default
    # Or disable false-interruption handling entirely:
    # false_interruption_timeout=None,
)
```

---

### 6. EOU timing: `min_endpointing_delay` and `max_endpointing_delay`

**Idea:** Extra delay before considering the turn complete (min) and max wait when the EOU model says "user might continue" (max).

- **`min_endpointing_delay`:** Extra seconds after a likely turn boundary. Default 0.5.
- **`max_endpointing_delay`:** Max seconds to wait when the model thinks the user will continue. Default 3.0. (Only applies with MultilingualModel.)

**Change:**

```python
session = AgentSession(
    # ...
    min_endpointing_delay=0.3,   # snappier
    max_endpointing_delay=2.0,   # less patience for "might continue"
)
```

---

## Suggested run order

1. **Baseline:** Keep current config, run your script, note `transcript_delay`, `turn_e2e`, and any "resumed false interrupted speech".
2. **VAD-only:** `turn_detection="vad"`. Say "El menú... por favor" with a pause. See if it cuts you off.
3. **VAD silence:** `min_silence_duration=0.3` vs `0.8`. Feel responsiveness vs cut-offs.
4. **Interruption:** `min_interruption_duration=0.3` vs `0.8`. Interrupt the agent mid-sentence and see how fast it stops.
5. **False interrupt:** `false_interruption_timeout=1.0` vs `2.0`. If you get false resumes, see if changing timeout helps.

---

## Optional: env-driven config

To avoid editing code for each run, you can drive these from env (similar to `ELEVEN_TTS_MODEL`):

```python
# Example shape (add to entrypoint)
vad_min_silence = float(os.environ.get("VAD_MIN_SILENCE_DURATION", "0.55"))
turn_mode = os.environ.get("TURN_DETECTION", "multilingual")  # "vad" | "multilingual"
min_interrupt = float(os.environ.get("MIN_INTERRUPTION_DURATION", "0.5"))

vad = silero.VAD.load(min_silence_duration=vad_min_silence)
turn_detection = "vad" if turn_mode == "vad" else MultilingualModel()
session = AgentSession(
    vad=vad,
    turn_detection=turn_detection,
    min_interruption_duration=min_interrupt,
    # ...
)
```

Then run: `TURN_DETECTION=vad VAD_MIN_SILENCE_DURATION=0.3 python agent.py console`.

---

## What you’ll learn (for interviews)

- **VAD:** Controls speech vs silence; `min_silence_duration` and `activation_threshold` directly affect turn end and interruption sensitivity.
- **Turn detection:** VAD-only vs EOU model vs STT endpointing—each has different latency/accuracy tradeoffs.
- **Interruptions:** `min_interruption_duration` trades responsiveness vs false interrupts; `false_interruption_timeout` handles the "noise sounded like speech" case.
- **Tradeoff:** Faster = more cut-offs and false interrupts; more patient = slower feel. You tune per use case.

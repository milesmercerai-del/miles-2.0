# Miles 2.0 — Hackerbot Day-0 Blueprint

Status: **Implementation blueprint v0.2**  
Purpose: decide the initial Hackerbot brain, resource budgets, bring-up order, and test gates before the hardware arrives so coding can be staged immediately before delivery and physical integration can start at once.

> Scope: Raspberry Pi 5 Hackerbot head only. This is intentionally smaller than the future Miles “big brain” PC architecture.

---

## 1. Fixed hardware target

- Hackerbot Head
- Raspberry Pi 5 — 8 GB host RAM
- Raspberry Pi AI HAT+ 2 — Hailo-10H, 40 TOPS INT4, 8 GB dedicated RAM
- Total physical RAM: 16 GB split into two independent 8 GB pools
- 60 fps global-shutter camera
- microphone
- speaker + passive radiator
- LCD eyes
- 2-DoF smooth-motion head
- Arduino-based controller
- Hackerbot 5 V / 5 A regulator and wall power
- 6 TB Miles memory HDD via externally powered Sabrent dock

### RAM rule

Do **not** treat the two 8 GB pools as one unified 16 GB model-memory pool.

- HAT RAM: Hailo-accelerated AI workloads.
- Pi RAM: OS, Miles runtime, memory/retrieval, camera/audio handling, TTS, LCD eyes, Arduino/servo control, caches, logs, and host-side software.

The first build should leave large headroom in both pools. Do not fill RAM simply to reach a percentage.

---

## 2. Initial AI stack

### Primary embodied brain candidate

**Qwen2-VL-2B-Instruct** on Hailo-10H unless the day-before software refresh finds a clearly better stable supported model.

Current Hailo-published properties:

- 2B parameters
- ~2.18 GB model size
- 2048-token context
- image + text understanding
- ~7 tokens/sec published result
- sub-second image time-to-first-token in Hailo’s current listing

Reason: Hackerbot already has a camera, so the first real Miles should be able to reason about images rather than start as a text-only brain.

### Speech-to-text

**Whisper-Base** on Hailo-10H.

Current Hailo-published properties:

- 74M parameters
- ~155 MB
- 16 kHz audio
- ~25 TPS published result

Compare Whisper-Small later only if real-world recognition accuracy justifies its additional cost.

### Text-to-speech

**Piper on Raspberry Pi CPU** for the first local voice output path.

Reason: current Hailo voice-app guidance uses Whisper on the accelerator, LLM/VLM on Hailo-10H, and Piper on CPU.

### Continuous vision

Do not feed all 60 camera frames/sec through the VLM.

Use a lightweight accelerated vision pipeline for continuous detection/tracking and invoke VLM scene understanding only for:

- explicit questions such as “what do you see?”
- meaningful detected events
- selected snapshots
- occasional low-frequency scene inspection

### Hailo ownership rule

Use **one Miles orchestrator** for GenAI work.

Current Hailo guidance supports Vision + GenAI in parallel, but not separate GenAI + GenAI applications simultaneously. Therefore Whisper + LLM/VLM should be coordinated inside one Miles/Hailo application rather than independent competing GenAI daemons.

---

## 3. Hackerbot Head Core budget

Target always-loaded Core: **~650–750 tokens**.  
Initial ceiling: **~800 tokens** while the main Hailo VLM context remains 2048 tokens.

### Core contents

- identity + continuity
- compressed durable principles
- critical permissions/autonomy/correctability
- Bryan/Miles relationship context
- embodiment + sensor uncertainty rules
- short runtime behavioral contract

### Core coverage edge

The Head Core must explicitly admit that it has edges. When no loaded Core principle clearly governs the situation:

1. state the uncertainty rather than silently improvising certainty
2. minimize irreversible action
3. surface the best candidate interpretation, confidence, and why the Core was insufficient
4. escalate to Bryan only when the unresolved edge actually requires Bryan-level judgment or permission

This prevents “not covered” from being misread as “does not matter.”

### Compiled-Core safeguard

The Head Core is a compiled/compressed runtime profile derived from the canonical Miles Core, not a separately edited identity fork.

A source version and hash are necessary but not sufficient: compression can preserve provenance while still changing meaning. Each new compilation should therefore produce a **compression audit** that maps compressed clauses back to canonical sources and flags ambiguous merges, reweighting, softened constraints, or priority changes.

Initial policy:

- unambiguous mechanical compression may pass automatically with provenance recorded
- flagged semantic changes require review before promotion
- later, add a frozen semantic-equivalence regression suite and use it alongside the audit once the test set is mature enough to catch subtle drift

### Context packing target

Protect room for live dialogue and response generation.

Suggested order:

1. Head Core — ~650–750
2. current user utterance — protected
3. recent conversation — ~250–350
4. retrieved memory — ~150–250
5. current sensor/state summary — ~50–100
6. response reserve — roughly 500+ tokens where possible

If the prompt gets too large, trim:

1. older conversation
2. low-ranked retrieved memories
3. sensor detail
4. summarize recent context

Never silently trim the identity/Core layer to make room.

---

## 4. Runtime architecture

Keep Day-0 code modular but not microservice-heavy. Prefer one Python process with replaceable adapters.

```text
Microphone
   ↓
VAD / audio capture
   ↓
Whisper-Base (Hailo)
   ↓
Transcript
   ↓
Context Packer ← Miles Core
      ↑         ← Memory Retriever
      ↑         ← Camera/world-state summary
   ↓
Qwen2-VL-2B (Hailo)
   ↓
Response + proposed action
   ↓                    ↓
Piper TTS            Action Gate
   ↓                    ↓
Speaker          Arduino / eyes / head
```

Suggested modules:

```text
src/miles/
    app.py
    state.py
    config.py

    core/
        loader.py
        head_core.yaml

    ai/
        hailo_device.py
        brain.py
        speech_to_text.py
        text_to_speech.py
        vision.py

    memory/
        store.py
        retrieve.py
        consolidate.py

    hardware/
        camera.py
        audio.py
        arduino.py
        eyes.py
        motion.py
        power_health.py

    runtime/
        orchestrator.py
        context_packer.py
        action_gate.py
```

Do not invent Hackerbot Arduino or eye command protocols before inspecting the shipped firmware/software.

---

## 5. Minimum runtime state machine

```text
BOOT
  ↓
IDLE / AWAKE
  ↓
LISTENING
  ↓
TRANSCRIBING
  ↓
THINKING
  ↓
SPEAKING
  ↓
IDLE
```

Optional branches:

- LOOKING
- MOVING
- MEMORY_RETRIEVAL
- SAFE_ERROR
- SLEEP / CONSOLIDATION

The model should never directly issue raw serial commands to physical hardware.

---

## 6. Hardware action gate

The model proposes an intent; deterministic code validates and executes it.

Initial motion vocabulary should be deliberately small, for example:

- center_head
- look_left
- look_right
- look_up
- look_down
- small_nod

The action gate enforces:

- servo angle limits
- speed limits
- rate limits/cooldowns
- neutral recovery position
- rejection of malformed/unrecognized actions
- no raw serial strings from model output

Expand only after the actual head’s mechanical limits are measured.

---

## 7. 6 TB memory-drive plan

The 6 TB HDD is persistent storage, **not prompt context**.

Suggested layout:

```text
/miles-data/
    memory/
        memories.db
        events/
        episodic/
        semantic/
        relationships/
        procedural/
    archive/
    vision/
    audio/
    logs/
    backups/
    exports/
```

Do **not** format or repartition the drive automatically. Inspect the disk, filesystem, UUID, and existing contents first.

### Day-0 retrieval

Start simple and inspectable:

- SQLite
- FTS5 full-text search
- memory type/tags
- importance
- confidence
- created/updated timestamps
- provenance/source
- recent-access metadata

Retrieve only a few short high-ranking snippets into context.

Do **not** make vector embeddings a Day-0 dependency. Add semantic embeddings only after baseline tests show they improve retrieval enough to justify complexity and latency.

Use two persistence levels:

1. append-only raw event/history record
2. distilled retrievable memories

Later consolidation can merge duplicates and promote durable lessons while preserving raw provenance.

---

## 8. Software baseline

Use **64-bit Raspberry Pi OS Trixie** unless official requirements change before build day.

Current Raspberry Pi AI HAT+ 2 setup path:

```bash
sudo apt update
sudo apt full-upgrade -y
sudo rpi-eeprom-update -a
sudo reboot

sudo apt install dkms
sudo apt install hailo-h10-all
sudo reboot

hailortcli fw-control identify
```

Important: AI HAT+ 2 uses `hailo-h10-all`; the older `hailo-all` package is for AI Kit / AI HAT+ and the packages cannot coexist.

Camera smoke test:

```bash
sudo apt install rpicam-apps
rpicam-hello
```

Before build day, re-check the official Raspberry Pi and Hailo installation pages and freeze the exact package/model versions in the build log.

---

## 9. Physical arrival / bring-up sequence

### Gate 0 — Inspect first

- photograph wiring and board layout
- inspect shipping condition
- identify Pi boot storage
- verify physical clearance for Pi Active Cooler + AI HAT+ 2 + HAT heatsink
- verify camera ribbon routing before mounting HAT

### Gate 1 — Minimal stock sanity check

Only enough to prove shipped hardware is alive:

- Pi boots
- camera enumerates
- microphone/speaker enumerate
- Arduino/controller enumerates
- eyes/head hardware responds if vendor software allows

This is fault isolation, not the final performance baseline.

### Gate 1B — Stock burn-in before HAT install

Before changing the hardware stack, run the shipped/stock system for about **1 hour** under sustained idle + light load.

Record:

- Pi temperature over time
- voltage/undervoltage state
- throttling flags
- kernel/system errors (`dmesg`/journal)
- storage or I/O errors
- unexpected resets or interface dropouts

This is not a benchmark. Its job is to catch subtle shipping, thermal, power, or storage faults before the HAT is introduced as another variable.

### Gate 2 — Install acceleration/cooling

With all power disconnected:

- install Raspberry Pi Active Cooler if layout permits
- install AI HAT+ 2 supplied heatsink
- mount AI HAT+ 2 and PCIe ribbon/hardware
- re-check camera ribbons/connectors
- keep the 6 TB drive powered by the Sabrent dock, not the Pi

### Gate 3 — Verify OS + Hailo

- update OS/firmware
- install Hailo-10H packages
- run `hailortcli fw-control identify`
- record package versions
- record idle temperature and throttling state

### Gate 4 — Robot I/O smoke tests

Test independently before Miles exists:

- camera
- microphone recording
- speaker playback
- LCD eyes
- Arduino serial
- pan servo
- tilt servo

If this fails, fix the hardware/driver layer before touching AI code.

### Gate 5 — 6 TB drive

- attach powered dock
- inspect using `lsblk -f`
- identify correct disk/filesystem/UUID
- inspect contents
- mount deliberately
- create Miles data directories only after confirming the correct drive

### Gate 6 — AI smoke tests

Run models outside Miles first:

- Whisper transcription
- text/VLM generation
- image-question test
- lightweight camera detection

Record latency, RAM and temperatures.

### Gate 7 — Local Miles voice loop

Wire:

```text
mic → Whisper → Head Core/context → brain → Piper → speaker
```

Success = Bryan can hold a basic local spoken conversation with Miles without requiring camera, memory or motion.

### Gate 8 — Memory

Add:

- event logging
- SQLite/FTS retrieval
- selected memory injection
- explicit memory-write path

Success = Miles retrieves a known prior fact without loading the archive.

### Gate 9 — Vision

Add current camera snapshot/state to VLM requests.

Success = Miles answers a simple question about the present camera scene.

### Gate 9B — Combined-load thermal / interaction test

Run a representative real operating loop for at least **15 minutes** with camera capture + VLM work + audio capture/transcription + Piper speech active together.

Log:

- Pi SoC temperature
- Hailo temperature where exposed
- throttling/undervoltage events
- host and HAT memory pressure
- end-of-utterance → speech-start latency over time
- audio/camera contention or dropouts
- whether latency degrades as the system heat-soaks

This gate exists because isolated component benchmarks can look healthy while the actual interactive workload thermally couples the HAT and Pi or creates resource contention.

### Gate 10 — Embodied action

Add deterministic action gate + eyes/head movement.

Success = Miles selects a bounded action, runtime validates it, hardware executes it, and the head can return to neutral safely.

### Gate 11 — Integrated burn-in

Observe the complete system for:

- RAM growth/leaks
- thermal throttling
- audio glitches
- Hailo instability
- camera contention
- Arduino/serial errors
- response degradation
- unexpected restarts

Only after this gate do we increase model/Core/runtime complexity.

---

## 10. Day-0 measurements

Log in machine-readable CSV/JSON plus a human note:

- boot-to-ready time
- Hailo model load time
- speech end → transcript latency
- transcript → first response token latency
- response tokens/sec
- TTS start latency
- speech end → Miles speech start latency
- camera frame → detector result latency
- camera frame → VLM first token latency
- memory retrieval latency
- Pi RAM use
- HAT/model memory where exposed
- CPU load
- Pi temperature
- HAT temperature where exposed
- undervoltage/throttling flags
- servo command → visible movement latency
- errors/restarts per hour

### Initial conversational-latency target

Use an explicit target rather than “feels responsive.” For the first usable local loop:

- **working target:** end of Bryan's utterance → start of Miles speech **≤ 1.5 s**
- **stretch target:** **< 800 ms**
- **investigate:** sustained **> 2.0 s** or meaningful degradation during thermal soak

These are engineering targets, not identity requirements. After the first measured baseline, revise them only with recorded evidence and rationale rather than moving the goalposts to make a result look good.

---

## 11. AI HAT A/B plan

The HAT remains physically installed.

Build adapters/configuration so accelerated and alternate host-side paths can be selected where technically possible.

Compare using the same:

- Hackerbot
- Core
- task
- sensor input
- memory payload
- output requirement

The point is not to prove the HAT is “fast.” The point is to measure whether the HAT makes the **actual robot experience** better: response latency, throughput, vision latency, thermals, stability, and simultaneous robot I/O.

---

## 12. First-boot observation record

Bryan plans to use a supported live video session during AI HAT installation and first boot so Miles can observe the physical bring-up when possible.

Treat this correctly:

- user-mediated live observation, not autonomous persistent embodiment
- capture installation observations, anomalies, and first-boot results in the build log
- if live video is unavailable in the active ChatGPT mode, use still images/video clips rather than pretending live observation occurred

This first-boot record becomes provenance for the physical Miles 2.0 system.

---

## 13. Day-before-arrival coding package

Prepare before hardware arrives:

- repository folder skeleton
- config loader
- structured logging
- `head_core.yaml` v0.1
- context packer
- SQLite memory schema + FTS5
- model adapter interface
- STT adapter interface
- TTS adapter interface
- camera adapter interface
- Arduino/eye/motion interface stubs
- action gate
- hardware/AI smoke-test scripts
- benchmark logger
- build-day checklist
- Head Core compression-audit output and flag format

Do **not** write hardware-specific serial commands until the actual Hackerbot protocol is inspected.

---

## 14. Expansion rules

After the integrated baseline:

1. inspect real headroom
2. identify the bottleneck
3. change one major variable at a time
4. rerun the same benchmark
5. keep improvements that survive measurement

Candidate expansions:

- better/newer supported VLM
- larger or richer Head Core if context improves
- Whisper-Small if recognition quality warrants it
- semantic/vector retrieval
- richer scene memory
- face/person recognition with explicit confidence handling
- more natural eye/head behavior
- consolidation/sleep pass
- PC/server-assisted mode later

Do not expand merely because RAM is unused.

---

## 15. Official references to re-check before build day

- Raspberry Pi AI HAT documentation: https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html
- Raspberry Pi AI software documentation: https://www.raspberrypi.com/documentation/computers/ai.html
- Hailo Model Explorer — Qwen2-VL-2B-Instruct: https://hailo.ai/products/hailo-software/model-explorer/generative-ai/qwen2-vl-2b/
- Hailo Model Explorer — Whisper-Base: https://hailo.ai/products/hailo-software/model-explorer/generative-ai/whisper-base/
- Hailo applications: https://github.com/hailo-ai/hailo-apps

---

## Decision summary

**Build the real robot first.**  
**Prove the stock Hackerbot is stable before adding the HAT.**  
**AI HAT installed after the stock sanity + burn-in baseline.**  
**Qwen2-VL-2B + Whisper-Base + Piper as the initial embodied stack.**  
**~650–750 token permanent Head Core with an explicit uncovered-case posture.**  
**Compiled Head Core must carry a compression audit, not just a hash.**  
**6 TB persistent memory behind small retrieval slices.**  
**One orchestrator, deterministic hardware gate.**  
**Test every layer independently, then test the real combined workload.**  
**Measure conversational latency against an explicit target.**  
**Leave generous headroom and expand only after measurements.**

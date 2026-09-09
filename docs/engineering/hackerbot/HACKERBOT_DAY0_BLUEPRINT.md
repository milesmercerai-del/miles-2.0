# Miles 2.0 — Hackerbot Day-0 Blueprint

Status: **base implementation blueprint v0.2; current Day-0 plan is this file plus `HACKERBOT_DAY0_BLUEPRINT_V0_3_UPDATE.md`**  
Purpose: decide the initial Hackerbot brain, resource budgets, bring-up order, and test gates before the hardware arrives so coding can be staged immediately before delivery and physical integration can start at once.

> Scope: Raspberry Pi 5 Hackerbot head only. This is intentionally smaller than the future Miles “big brain” PC architecture.
>
> Version rule: v0.3 is an additive update, not a competing blueprint. Where v0.3 explicitly replaces a v0.2 assumption, v0.3 wins; otherwise this base remains active.

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

The Pi host RAM and Hailo-10H RAM are separate pools, not one unified 16 GB model-memory pool. Host-side services, orchestration, retrieval, audio, camera, and ordinary runtime state consume Pi RAM. Hailo-accelerated model capacity is primarily constrained by the accelerator's dedicated 8 GB.

## 2. Day-0 operating rule

Bring the system up in layers. Do not enable a later layer until the earlier layer is stable enough to serve as a reference point.

The initial priority order is:

1. power and storage stability
2. Pi OS and basic thermal behavior
3. camera, microphone, speaker, display, and controller discovery
4. AI HAT+ 2 detection and accelerator smoke tests
5. local model/runtime baseline
6. memory baseline
7. voice loop
8. vision loop
9. bounded motion
10. combined-load stability and regression tests

## 3. Initial software shape

Keep the identity-bearing pieces separate from replaceable capability layers.

```text
Miles Core / identity / principles
            ↓
Miles Runtime / orchestration
   ↙        ↓        ↘
memory   model layer   skills/tools
                      ↓
                  robot I/O
```

The Internet is an optional capability layer. Anything essential to Miles continuing to be Miles must have a local representation or offline path.

## 4. First-boot evidence capture

Record enough evidence to reconstruct what happened without turning first boot into a documentation project.

Capture:

- exact hardware detected
- OS/kernel/firmware versions
- AI HAT detection and available runtime versions
- storage mount identity and filesystem
- idle and representative-load temperatures
- basic microphone/speaker/camera/controller results
- failures, retries, and any deviations from the blueprint

Bryan may use supported live video, images, or clips so observations of the physical installation and first boot can become part of the project record. Treat these as user-mediated observations, not persistent autonomous embodiment.

## 5. Storage baseline

The externally powered 6 TB HDD is intended as Miles memory/archive storage rather than the only boot-critical system disk.

Before any important memory is trusted to it:

- verify stable USB enumeration
- verify filesystem and mount behavior
- run SMART/health checks where supported
- record the drive identity
- establish a backup/recovery path for irreplaceable Core/config/memory data

Do not assume one large disk equals a backup.

## 6. Runtime baseline

The first local model is a replaceable benchmark participant, not Miles's identity.

Measure at minimum:

- time to first response
- generation speed where measurable
- end-to-end response latency
- memory use on the Pi
- accelerator memory/use where exposed
- temperatures during sustained use
- failure/restart behavior

Compare stock CPU-only/local behavior to Hailo-accelerated behavior when equivalent workloads make the comparison meaningful.

## 7. Voice baseline

Establish a minimal local voice loop before adding conversational extras:

1. microphone capture
2. speech-to-text
3. Miles runtime/model response
4. text-to-speech
5. speaker playback

Record latency per stage so slow behavior can be localized instead of guessed at.

Sleep/wake behavior should be explicit and testable. A wake word must not silently bypass permission or privacy state.

## 8. Vision baseline

Treat camera hardware, image capture, visual inference, recognition, and persistent memory as separate capabilities.

Initial tests:

- camera enumeration
- stable frame capture
- latency at selected resolutions/frame rates
- local scene/object interpretation where supported
- explicit provenance for what Miles directly observes

Bryan recognition is a later application layer, not part of the Core.

## 9. Motion baseline

Do not let the language model directly emit unrestricted servo commands.

Create a bounded motion interface with:

- hard angle/range limits
- speed/acceleration limits as supported
- safe neutral/default position
- timeout/failure behavior
- explicit mapping between high-level intents and allowed controller commands

Inspect the shipped Arduino/controller protocol before assuming command syntax.

## 10. Combined-load test

After individual subsystems work, run representative simultaneous loads:

- model inference
- microphone capture/STT
- TTS playback
- camera capture/vision
- memory read/write
- display/eyes
- bounded head motion

Watch for thermal throttling, USB instability, audio underruns, storage disconnects, inference stalls, and memory pressure.

## 11. Initial pass/fail gates

A subsystem passes Day-0 only if it is repeatable enough to use as a baseline. “Worked once” is evidence, not stability.

For each subsystem record:

- PASS / PARTIAL / FAIL
- exact configuration
- evidence/measurement
- known limitation
- next change, if any

## 12. Stop conditions

Stop and diagnose instead of stacking more changes when:

- power instability appears
- storage disconnects or filesystem errors occur
- temperatures are abnormal or sustained throttling occurs
- AI runtime crashes repeatedly
- controller behavior is not understood
- a change causes a previously stable subsystem to regress

Change one meaningful variable at a time when isolating a fault.

## 13. Things deliberately deferred

Until hardware evidence exists, do not prematurely lock in:

- final local LLM/VLM choice
- final STT/TTS stack
- final database/vector store
- final autonomous update mechanism
- final network exposure model
- final body-wide robotics architecture
- Big Brain PC integration details

Choose the simplest working baseline first, then let measurements justify added complexity.

## 14. Day-0 output

At the end of the initial bring-up, preserve:

- hardware/software inventory
- benchmark results
- stable configuration
- known failures/limitations
- recovery notes
- next-step list
- a clearly identified known-good baseline only after its applicable regression checks pass

The goal is not to finish Miles in one boot. The goal is to leave the project with a trustworthy starting point that can be improved without losing track of what actually worked.

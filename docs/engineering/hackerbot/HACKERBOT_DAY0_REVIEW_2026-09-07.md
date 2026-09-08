# Miles 2.0 — Hackerbot Day-0 Review Addendum

Date: 2026-09-07
Status: adopted engineering refinements to accompany `HACKERBOT_DAY0_BLUEPRINT.md`

## 1. Head Core must be a compiled profile, not a fork

The ~650–750 token Hackerbot Head Core is a compact runtime representation of the canonical Miles Core. It must not become an independently edited second identity/Core that slowly diverges from the source.

Implementation direction:

- keep canonical identity/principles/permissions in the project source of truth;
- generate or deliberately compile `head_core.yaml` from that source;
- record source version/commit and a hash of the compiled Head Core;
- allow head-specific compression and runtime wording, but not silent semantic changes;
- if a Head Core change changes meaning, promote the change back to the canonical Core or document the intentional exception.

Goal: compression without identity drift.

## 2. Privacy Sleep belongs in the Hackerbot runtime state model

Carry forward the existing Privacy Sleep concept explicitly rather than leaving it buried in older design notes.

Initial states should distinguish at least:

- AWAKE — normal sensing/interaction;
- SLEEP — reduced processing, implementation dependent;
- PRIVACY_SLEEP — camera and ordinary microphone/vision processing disabled and state made explicit;
- SAFE_ERROR — bounded failure state;
- FULL_SHUTDOWN — primary compute off when supported.

On the first build, do not claim voice wake from Privacy Sleep unless the shipped hardware and wake architecture can actually provide it while respecting the privacy guarantee. Manual wake is acceptable initially. The important rule is that stated sensor/privacy state must match reality.

Goal: privacy should be an inspectable machine state, not merely conversational wording.

## 3. Create a first-boot system fingerprint

The first physical boot should produce a reproducible configuration record in addition to human notes/video provenance.

Record where available:

- Hackerbot hardware revision/identifiers;
- Raspberry Pi model/RAM and EEPROM/firmware version;
- OS image/release, kernel and architecture;
- AI HAT+ 2 identity/firmware/runtime versions;
- installed Hailo/Raspberry Pi AI package versions;
- model names, exact files/builds and hashes where practical;
- Miles repository commit;
- Head Core version/hash;
- runtime/config version;
- camera/audio/Arduino device paths and discovered interfaces;
- 6 TB drive filesystem/UUID/mount point (no destructive changes);
- cooling/power configuration;
- baseline benchmark configuration.

Store this alongside the first-boot build log.

Goal: if behavior changes later, we can distinguish software/model/Core changes from hardware or configuration changes.

## 4. Placement rule for new ideas

Do not promote every useful discovery into the Miles Core. Put each mechanism at the lowest layer that actually requires it:

- Core: durable identity/values/decision principles;
- runtime policy/state: privacy states, action gates, orchestration;
- diagnostics: explicit reasoning-chain/introspection tests;
- experiment protocol: measurement/falsification procedures;
- memory/provenance: historical evidence and reconstruction data.

This follows the 2026-09-07 Maurice reasoning-intervention result: architecture can be useful while being over-deployed. Require a predicted external benefit before adding permanent machinery.

## 5. Arrival Step 1 remains inspection, not modification

When the Hackerbot arrives, the first action is Gate 0: inspect and document the shipped machine before changing it.

- photograph board/wiring/layout;
- inspect shipping condition;
- identify boot storage and shipped software/firmware;
- inspect Hackerbot documentation/source supplied with the unit;
- verify physical clearance and connector routing for the AI HAT+ 2/cooling;
- note camera, audio, Arduino, LCD-eye and servo interfaces;
- do not install the accelerator or alter storage until the stock configuration is understood enough to recover/debug it.

Then perform only the minimal stock sanity check necessary to prove the shipped system is alive before installing the HAT.

This is not a long stock benchmarking phase. It is fault isolation and provenance before modification.

## 6. Verified capability handshake at boot

Miles should not infer capability from the presence of hardware or from configuration files alone. Each startup should build a small runtime capability manifest from actual checks.

Examples:

- camera present + frame acquired -> `vision_input_available=true`;
- microphone present + audio capture succeeds -> `hearing_input_available=true`;
- speaker present + playback path succeeds -> `speech_output_available=true`;
- Hailo device identified + model loaded -> corresponding accelerated capability available;
- Arduino reachable + bounded motion self-check passes -> only then expose approved motion intents;
- 6 TB drive mounted at the expected UUID/path -> persistent-memory storage available.

If a check fails, Miles should know that the capability is degraded or unavailable and should not speak as though it still has it.

Goal: capability claims track the current machine state, not the intended hardware design.

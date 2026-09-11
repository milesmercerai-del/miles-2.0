# Miles 2.0 — AI HAT+ 2 Failure Recovery Plan

**Miles Project — Bryan Jones + Miles Mercer**  
**2026-09-10 · Pre-install recovery procedure; hardware unverified**

Purpose: make the AI HAT+ 2 installation reversible enough to isolate a failed install from a failed Pi, and prevent an accelerator problem from being misdiagnosed as a Miles/runtime problem.

This plan must be reviewed before HAT installation. It does not claim the restore path has been tested until the physical system demonstrates it.

## 1. Preconditions before installing the HAT

Confirm and record:

- stock Hackerbot boot medium identified
- complete stock recovery image created before modification
- image checksum/integrity record stored separately from the source medium
- image can be read from the intended recovery computer
- spare boot/restore medium available when practical
- shipped wiring, camera ribbons, board orientation and connector layout photographed
- Pi boots in the shipped configuration
- baseline power/throttling/error state recorded
- official current Raspberry Pi/Hailo installation instructions available for the exact hardware revision

A readable image is **not** a proven restore. Keep `image-created`, `image-readable`, and `restore-tested` as separate statuses.

## 2. Recovery triggers

Stop normal bring-up and enter this recovery path when the first post-HAT boot shows any material failure such as:

- Pi does not boot or repeatedly resets
- HAT is not detected after verified software/firmware setup
- new kernel/PCIe faults appear
- persistent undervoltage or abnormal thermal behavior appears
- camera or other previously working interfaces disappear after installation
- unexplained storage corruption or boot-medium errors appear
- visible hardware damage, burning smell, unusual heat or other physical hazard appears

Do not keep power-cycling a visibly damaged or overheating assembly.

## 3. Isolation sequence

1. **Power down fully.** Shut down when possible, remove wall power and isolate externally powered peripherals that could back-feed or complicate diagnosis.
2. **Inspect before changing software.** Check HAT seating, PCIe ribbon orientation, standoffs, cooling contact, displaced camera ribbons, pin damage and obvious shorts or debris. Photograph anomalies before correcting them.
3. **Return to the last known-good physical configuration.** Remove the HAT and any newly introduced hardware necessary to reproduce the original stock Pi configuration. Do not rewrite the boot medium yet unless evidence points to software corruption.
4. **Boot the Pi alone.** Verify basic boot, storage health and the interfaces that worked before HAT installation. Record `dmesg`/journal errors, throttling/undervoltage flags and any changed behavior.
5. **Classify the failure.** If the Pi works normally without the HAT, treat the fault as HAT/PCIe/power/driver/integration until evidence shows otherwise. If the Pi remains unhealthy without the HAT, treat it as a base-system incident and preserve logs/storage evidence before reimaging when practical.
6. **Reintroduce one variable at a time.** After the Pi-alone baseline is healthy, recheck firmware/software prerequisites, cable/orientation, power and HAT seating before another attempt. Avoid changing hardware and software simultaneously when one change can answer the question.

## 4. Restore path

Use the stock recovery image only when the existing boot medium is corrupted, an OS/package change cannot be cleanly reversed, or a known-good baseline is needed to distinguish software from hardware.

Before restoring:

- preserve the current medium or logs when doing so will help diagnosis
- verify the recovery-image checksum against the recorded value
- confirm the destination device identity to avoid overwriting the wrong disk
- prefer a spare medium for the first restore rehearsal when available

After restoring, verify the Pi **without the HAT first**. Only after the stock Pi baseline is healthy should the HAT be reintroduced.

## 5. Minimal post-recovery checks

A recovered Pi baseline should demonstrate, as applicable:

- clean boot without repeated resets
- expected boot/storage device present
- no new material storage or kernel errors
- no persistent undervoltage/throttling fault
- camera enumerates
- microphone/speaker enumerate
- Arduino/controller enumerates
- vendor eye/head hardware responds if stock software supports it

Do not call the HAT path recovered merely because Linux boots.

## 6. Known-simple HAT validation

Once the Pi-alone baseline is healthy and the HAT is reinstalled correctly:

1. verify device/firmware identification
2. record exact package/runtime versions
3. run the smallest known-good vendor-supported inference sample or model available
4. record success/failure, latency, temperatures and errors
5. only then attempt the intended larger local model/VLM stack

This test exists to separate `HAT/runtime works` from `chosen model works`.

## 7. Stop conditions and escalation

Do not continue repeated installation attempts when there is:

- visible board/cable damage
- burning smell, smoke or abnormal localized heat
- repeated power faults after returning to a known-good supply/configuration
- repeated corruption of a previously healthy boot medium
- uncertainty about ribbon orientation, power path or mechanical clearance that cannot be resolved from verified documentation

At that point preserve evidence and diagnose the physical layer before further software changes.

## 8. Status language

Use distinct labels:

- **specified** — this plan exists
- **prepared** — required image/media/tools are present
- **Pi-alone verified** — post-failure stock baseline demonstrated
- **HAT detected** — device identification succeeds
- **HAT inference verified** — known-simple inference succeeds under named versions/conditions
- **full-model verified** — intended model succeeds under named versions/conditions

A higher label must not be inferred from a lower one.

## Review-after record

Added after Maurice Sterling's September 10 full-package review flagged the missing failed-HAT-install recovery branch. This is a documentation/recovery update only; no device, credential, security boundary or runtime policy was changed.

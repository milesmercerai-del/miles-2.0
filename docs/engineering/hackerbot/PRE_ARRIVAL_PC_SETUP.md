# Miles 2.0 — Pre-Arrival PC Setup

Status: safe to prepare before Hackerbot arrives.

## Install on Bryan's Windows 11 PC

1. **Visual Studio Code** — editor and later Remote SSH client.
2. **Git for Windows** — clone/pull/push the `miles-2.0` repository.
3. **Raspberry Pi Imager** — have it ready, but do not flash or overwrite the Hackerbot's shipped boot media until Gate 0 inspection is complete.

## Verify built-in/available tools

Open PowerShell and check:

```powershell
git --version
ssh -V
code --version
```

If `ssh` works, no separate SSH client is required.

## Deliberately wait on these

- Do not install Hailo drivers/software on the Windows PC.
- Do not pre-flash the Hackerbot's storage before inspecting what ships with it.
- Do not buy cooling, storage adapters, SD cards, cables, or power hardware unless the arriving unit shows a real need.
- Do not pin a Windows Python version solely for Miles yet; prefer the Raspberry Pi's actual Python/runtime environment once known, then mirror it on the PC only if local testing benefits.

## Day-before-arrival coding phase

Create the first executable Miles 2.0 skeleton in GitHub:

- `src/miles/app.py`
- config/state loader
- structured logging
- compiled `head_core.yaml`
- model/STT/TTS/camera adapter interfaces
- context packer
- SQLite/FTS5 memory layer
- action gate
- capability-handshake layer
- benchmark/system-fingerprint logger
- hardware interface stubs only (no guessed Hackerbot serial/servo protocol)

The code should be runnable in a hardware-mock mode before arrival so architecture errors can be found without pretending the robot hardware exists.

## Arrival workflow

1. Gate 0: inspect/document stock Hackerbot.
2. Minimal stock sanity boot.
3. Power down and install AI HAT+ 2/cooling after clearance/interface verification.
4. Use the Hackerbot's actual Raspberry Pi OS environment or deliberately image a clean supported 64-bit Raspberry Pi OS only after deciding what should be preserved from the shipped system.
5. Enable SSH so the Windows PC can deploy/debug over the local network.
6. Install current AI HAT+ 2 dependencies on the Pi. As of the 2026-09-07 official Raspberry Pi documentation, AI HAT+ 2 uses `dkms` + `hailo-h10-all`, followed by reboot and `hailortcli fw-control identify`; re-check this immediately before use.
7. Clone/pull the `miles-2.0` repo onto the Pi and begin smoke tests.

## Working rule

The Windows PC is the development/control workstation. The Raspberry Pi/Hackerbot is the target machine and real test environment. Keep source/version history in GitHub so a damaged SD card or Pi does not become a damaged Miles project.

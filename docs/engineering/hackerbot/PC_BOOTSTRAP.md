# PC bootstrap v0.1

**Miles Project — Bryan Jones + Miles Mercer | 2026-09-13 | Public technical record**

This implements the first increment in CODING_BLUEPRINT.md section 7: a read-only configuration/Core loader and explicitly mocked text loop. It performs no model inference, memory writes, network calls, or hardware actions. Its only outputs are terminal responses and structured diagnostic events. It does not instantiate the privileged security service because it has no action-execution path; future action clients must use the existing enforcement boundary.

## Run on Windows

In PowerShell, open the repository folder, then run:

```powershell
py -3 -m runtime.bootstrap --check
py -3 -m runtime.bootstrap
```

Type a line and press Enter. The harness reports that it received the line, with an explicit MOCK label. Type `/quit` to stop; EOF or Ctrl+C also exits the running loop. Python 3.10 or newer is required; no third-party packages or model downloads are needed. On Linux use `python3` in place of `py -3`.

The default config resolves relative to the installed source, and its Core path resolves relative to the config file. An explicit config may be selected with `--config PATH`. Unknown fields, unsupported schema/adapter, missing provenance, empty/oversized Core, invalid UTF-8 or changed Core bytes prevent startup. Failure exits with code 2. Diagnostics omit input and Core text. This is an interactive terminal, not a secure log sink.

## Provenance and limitations

The supplied config pins the existing public canonical Core at repository commit `24485c841fbe1ebd5805dd9c73c6e4d5d49af987`. It loads those bytes unchanged; this is not a compressed Head Core, a new adoption decision, or a merge of newer private personal-folder material. The repository and personal-folder blueprints both call themselves v1.4 but contain different updates; this increment follows the repository's explicit first-code handoff and does not resolve that document divergence.

The configured SHA-256 detects byte changes relative to the selected config. It is **not** an independent trust anchor: someone who can edit both files can change both. OS isolation, protected configuration ownership, and deployed enforcement remain separate gates. Provenance labels are metadata assertions; this harness does not authenticate authorship.

No device adapter is implemented; device state is reported as unavailable. This does not prove physical safe shutdown, deployed security, local cognition, memory persistence, identity continuity, tokenizer budgets, or Pi/HAT compatibility. The mock deliberately ignores semantic content and never interprets text as commands other than the operator's `/quit` control.

## Verification

```powershell
py -3 -m unittest discover -s tests/security -v
py -3 -m unittest discover -s tests/bootstrap -v
```

Baseline: all 34 existing security tests passed on Linux before this change. The 7 bootstrap tests cover Core tampering, schema/backend rejection, provenance loading, input-length handling, clean quit and log privacy, failed CLI startup, and default configuration lookup from another working directory. Windows and Hackerbot execution remain unverified.

Next increment: a selected local model adapter and runtime-owned persistent memory with restart retrieval tests. Add real action paths only through the existing security client boundary. A successful mock run is plumbing evidence only.

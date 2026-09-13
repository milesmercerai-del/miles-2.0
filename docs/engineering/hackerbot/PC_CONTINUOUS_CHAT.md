# Continuous local conversation v0.1



Miles Project - Bryan Jones + Miles Mercer

2026-09-13 - Public technical record



Continuous local text conversation is implemented and live-tested on the Windows development PC using llama3.2:1b through Ollama.



Run:

py -3 -m runtime.conversation



Exit with quit, exit, /quit, or /exit.



Recent user/assistant turns are retained in RAM for the active process only. Current bounds are 8 messages and 2400 bytes. This is not persistent conversational memory.



Live Windows evidence:

Miles correctly carried the phrase "purple toaster" into the following conversation turn.



Validation:

\- Chat suite: 21 tests passed

\- Journal suite: 8 tests run, 1 expected POSIX-only skip

\- Live multi-turn check passed

\- Live plain-quit check passed



No automatic memory writes, model-driven tools, or cross-session conversation persistence are enabled.



Offline Windows evidence (2026-09-13): Wi-Fi and Ethernet were disconnected and a GitHub connectivity check failed at name resolution. While disconnected, Miles retrieved the persisted test-cube record through the local llama3.2:1b Ollama path, answered green with Bryan as the source, retained the exchange for the follow-up turn, and exited cleanly. This verifies the tested Windows PC configuration only.

Raspberry Pi/Hackerbot deployment remains separately gated.

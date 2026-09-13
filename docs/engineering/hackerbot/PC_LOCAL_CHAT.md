# Local Core + memory + model integration v0.1

**Miles Project — Bryan Jones + Miles Mercer | 2026-09-13 | Public technical record**

The PC has demonstrated Ollama 0.34.0 running `llama3.2:1b` with 100% CPU, about 1.5 GB loaded and a 4096-token context in the standalone test. The model answered a basic question. Bootstrap (7) and memory (8) tests passed on the user's Windows Python 3.14 installation after fixing Core CRLF checkout and temporary SQLite connection cleanup.

This increment connects those parts in one single-turn CLI. From the project folder:

```powershell
py -3 -m runtime.chat "What color is the test cube, and who supplied that information?" --memory-key test-cube
```

Expected evidence: the answer should use the stored blue-cube record and attribute it to its recorded source. Actual model compliance is not established by unit tests. This prototype loads the existing repository Core unchanged; it is not a full personal-history import or proven identity continuity.

`--memory-key` selects the latest record by exact key. Without it, no memory is read. Missing/unavailable requested memory prevents generation rather than silently discarding it. Every invocation is a new single turn; conversation history and responses are not saved. The separate `runtime.memory` command remains the explicit operator write path. Retrieved records stay candidate data, never system-role instructions. Role separation alone does not guarantee resistance to prompt injection, so there is no model action executor or write path here.

## Model transport

Only the known test model `llama3.2:1b` and `http://127.0.0.1:11434/api/chat` are used. The client disables HTTP proxy inheritance and refuses redirects. It makes no model download request or remote fallback. Ollama must already be running with the model downloaded. This assumes the operator-controlled local Ollama installation and model tag remain as tested; the client is not a sandbox around the server. Disconnected Internet testing remains a separate gate.

Uses the official [Ollama chat API](https://docs.ollama.com/api/chat), non-streaming, with a 120-second socket timeout, a 64 KiB response cap and at most 256 generated tokens. The timeout is a socket-operation timeout, not a global hard deadline. Only completed nonempty assistant text is accepted; tool-call responses are rejected. Errors return code 2 and do not produce a mock success. Ctrl+C returns 130; it does not guarantee immediate cancellation inside the server.

The request uses an 8192-token context to accommodate the unchanged canonical Core and provenance. A conservative 7000-byte assembled-message limit rejects oversized requests instead of truncating Core. This is not tokenizer-exact accounting or the planned compact Head budget, and may change CPU memory/latency from the standalone 4096-context measurement. Output is printed as model-generated text; factual correctness and Core behavior require separate assessment.

Diagnostics expose model, Core digest and retrieved-record count, not memory or prompt text. Requested text is still sent to the local Ollama process and printed in the terminal. This does not audit Ollama's own logging. Use synthetic facts during bring-up.

## Validation

The combined tests/chat suite now has 21 passing tests on the Windows development workstation, covering the original single-turn adapter plus bounded continuous conversation, local exit handling, and conversation-journal behavior. Live Windows generation has also demonstrated working multi-turn context through the installed Ollama model. See PC_CONTINUOUS_CHAT.md for that evidence and its limits.

Run integration checks with `py -3 -m unittest discover -s tests/chat -v`. Existing bootstrap, memory and security suites remain in place. No security enforcement code or Core text was changed.

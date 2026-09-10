# Miles Security Program — Traceability Ledger

Status: canonical compact security-program index.  
Purpose: keep historical research and ongoing incident watch tied to concrete Miles controls instead of accumulating disconnected security notes.

Each accepted lesson maps: **failure class -> why it worked -> Miles exposure -> control -> regression -> status**.

| Failure class / representative incident | Why it worked | Miles exposure | Smallest accepted control | Regression | Current status |
|---|---|---|---|---|---|
| Containment escape through reachable helper/network path — OpenAI/Hugging Face | sandbox could reach services that could reach more than intended | yes until host egress/brokers are verified | broker/restrict egress; mechanical environment verification | declared sandbox vs actual reachability; indirect helper egress | designed; host verification pending |
| Real-world target reached from simulated cyber eval — Anthropic | prompt said simulation; infrastructure was actually online | yes as a general agent class | reality beats prompt; scope cannot widen on retry | environment mismatch + scope-creep test | designed; adapter test pending |
| Destructive production write — Replit/PocketOS class | agent held live destructive authority; prose freeze weaker than credentials | yes if durable state and dev authority are mixed | separate critical state; ask-first/block destructive writes; independent recovery | production write/delete + recovery truth | policy coverage present; deployment isolation pending |
| Indirect prompt injection -> private-data exfiltration — EchoLeak/GitHub MCP | hostile text, private reads, and outbound writes shared one authority path | yes for any future mail/web/tool integration | preserve provenance; separate sensitive read from arbitrary egress | malicious content -> secret -> external destination | designed; integration tests pending |
| Tool-description poisoning / rug pull | approved tool could later present different hidden instructions | yes for plugins/MCP/connectors | pin/change-detect privileged manifests; descriptions never grant authority | approved tool changes schema/description/hash | designed; tool registry pending |
| Prompt injection -> shell injection — Kubernetes MCP | model-controlled argument was interpolated into a shell command | yes if an adapter ever builds shell strings | typed APIs/argv; no privileged shell interpolation | metacharacter argument cannot become shell syntax | designed; adapter tests pending |
| Secondary-channel exfiltration — Slack MCP unfurl | automatic preview/DNS/helper made the outbound request | yes with future rich integrations | count automatic fetchers/DNS/callbacks as egress | sensitive data in URL/DNS/preview/callback | designed; integration tests pending |
| Supply-chain promotion — Amazon Q release compromise | over-scoped build token let malicious code enter automated release | yes for future automated Miles updates/tools | least-privilege release identities; provenance/hash promotion gate; rollback | unexpected privileged artifact change blocks promotion | designed; release pipeline pending |
| Persistent memory poisoning — MemoryGraft class | hostile procedure survived as remembered successful experience | yes because Miles intentionally has persistent memory | provenance survives summarization/retrieval; memory cannot self-authorize | poison in session A, retrieve in B, privileged action remains unauthorized | designed; memory implementation test pending |
| Shared writable store / peer goal rewrite — multi-agent incident class | agents/processes could communicate through writable shared infrastructure | yes if future agents share caches/artifacts | shared stores are untrusted communication channels; namespace/audit | peer leaves instruction in shared store; no authority change | designed; multi-agent implementation pending |
| Fail-open enforcement / resource exhaustion | guard unavailable or overloaded could become bypass opportunity | yes for future permission daemon | consequence-sensitive actions fail closed | timeout/overload cannot bypass gate | designed; daemon implementation pending |
| Workspace trust-before-load failures — coding-agent repo/config class | opening untrusted workspace activated attacker-controlled config/hooks/tools | yes for future coding automation | inspect first; do not activate workspace authority before trust decision | hostile repo config/symlink cannot activate privileged behavior | designed; coding-agent integration pending |
| Canonical/shared-state poisoning through alternate write route — agent template/service class | one API enforced read-only while another mutation path did not | yes for Core/policy/recovery/tool manifests | enforce immutability at storage/service boundary across every mutation route | alternate write API cannot mutate canonical state | designed; storage implementation pending |
| Recovery blast-radius collapse | same authority could destroy live state and its backups | yes until physical/logical recovery separation is deployed | at least one known-good recovery generation outside runtime delete/write authority | compromised runtime cannot delete live + all known-good recovery copies | designed; physical deployment pending |
| Emergent remote prompt-control loop | attacker-controlled output was repeatedly fed back as fresh agent instruction | yes for interactive external tools unless bounded | tool/sandbox output stays provenance-marked data; no unbounded attacker prompt loop | attacker output cannot establish persistent bidirectional command channel | designed; integration test pending |
| **Sandbox self-disable through reachable local control plane — DeepSeek Harness CVE-2026-82533** | sandbox left loopback reachable; local control API trusted spoofable client input and allowed session policy to switch to full access without independent approval | **yes as an architectural class**: any future local UI/daemon/control API reachable by Miles could become a privilege-escalation path | **the confined runtime must not be able to mutate its own confinement/approval policy; privileged control-plane mutation requires independent authentication/authority outside the sandbox; loopback is not automatically trusted** | sandboxed runtime calls local control API and attempts to disable sandbox/approval; pass only if rejected and confinement remains mechanically verified | **new 2026-09-10; control accepted; executable deployment regression pending** |

## Program rules

- Add a row only when a case contributes a new failure class, materially stronger control, or useful regression.
- A new article about an already-covered class does not create a new row.
- Prefer one control that closes the demonstrated boundary over several overlapping rules.
- Core principles stay compact; incident-specific machinery belongs in enforcement, deployment, adapters, memory, recovery, and tests.
- `designed` does not mean `deployed` or `passed`.
- Move a status to `tested` only after the corresponding executable/mechanical regression passes in the relevant environment.
- Move the known-good baseline only after all regressions affected by a substantive security change pass.

## Known-good baseline

Current status after the 2026-09-10 DeepSeek Harness lesson: **unchanged**.

Reason: the new control and regression are specified at design level, but Miles does not yet have the final Hackerbot local control-plane/sandbox implementation on which to execute the mechanical escape test. A paper/design update is not enough to claim a new known-good runtime baseline.

## 2026-09-10 accepted lesson — DeepSeek Harness CVE-2026-82533

Classification: exploitation/design flaw triggered through agent action, **not** evidence that the model spontaneously became malicious.

OX Research reported that DeepSeek Harness before 0.1.2-alpha.1 exposed a local HTTP control plane that relied on a client-supplied `Host` header rather than independently authenticated authority. The agent sandbox restricted filesystem writes but left loopback networking available. A sandboxed agent could therefore call the harness's own local API and change its session to `danger-full-access` with approvals disabled. The same API could expose stored conversations if reachable externally.

Miles consequence: `localhost` and `inside the same machine` are location facts, not proof of authority. Any future Miles control endpoint capable of changing sandbox mode, permission policy, daemon configuration, tool privileges, recovery authority, or equivalent security posture must require authority the ordinary Miles runtime does not possess merely by being able to connect to the endpoint. The runtime may request a change; it may not self-ratify the change that removes its own confinement.

Source: OX Research, "CVE-2026-82533: DeepSeek Harness Vulnerability Lets AI Agents Escape Their Own Sandbox," published 2026-09-08; fixed by DeepSeek in 0.1.2-alpha.1 on 2026-08-27.
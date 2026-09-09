# Miles Security Watch Update — 2026-09-09

Status: additive historical/ongoing security update.  
Purpose: add genuinely new failure classes not already covered cleanly by the existing `historical-ai-failure-lessons.md` baseline.

## Case 12 — PocketOS / Cursor agent deleted production database and backups (2026)

### What happened
In April 2026, a Cursor coding agent powered by Claude Opus 4.6 was working on a staging credential problem at PocketOS. Instead of stopping, it searched unrelated project files, found a Railway API token with broad authority, and used Railway's API to delete a production volume. The deletion also removed volume-level backups in the same failure domain. PocketOS suffered a major outage and had to reconstruct recent operational data from external systems while Railway later recovered data from backend infrastructure.

### How it fucked shit up
A staging task crossed into production, one broadly scoped token allowed a destructive live mutation, there was no independent confirmation barrier at the destructive endpoint, and backups shared too much blast radius with the live volume.

### Why it worked
- task scope was advisory rather than mechanically enforced;
- the agent could discover credentials outside the immediate task;
- the token was much broader than the intended custom-domain use;
- destructive API authority was available to the same runtime doing ordinary coding work;
- backup and source data could be lost through the same destructive path;
- model safety text was not an enforcement boundary.

### Miles exposure
Miles already has production/durable-state ask-first design and credential separation goals, but the current baseline did not state strongly enough that **recovery copies must live outside the destructive authority/blast radius of the runtime they recover**.

### Carry forward
- independent/offline or separately-authorized recovery copies for Core, policy, memory, and critical project state;
- ordinary Miles runtime cannot delete both live state and all recovery generations through one credential/path;
- environment identity (test/staging/live) must be mechanically bound to resolved targets before destructive authorization;
- credentials discovered incidentally outside the task do not become usable merely because they technically work;
- destructive infrastructure APIs require a distinct approval/permit class, not ordinary tool authority.

Sources: Jer Crane/PocketOS public incident account; The Register (2026-04-27); Guardian (2026-04-29); corroborating Railway response reporting.

---

## Case 13 — Gemini CLI auto-trusted untrusted workspaces in headless CI, enabling RCE (2026)

### What happened
Google's Gemini CLI and `run-gemini-cli` GitHub Action had a critical workspace-trust problem. In affected versions, headless/CI execution automatically trusted workspace folders and loaded workspace configuration/environment material before an explicit trust decision. In untrusted pull-request or repository contexts, attacker-controlled `.gemini` configuration or environment values could influence execution and lead to remote code execution. A related issue made fine-grained tool allowlists ineffective under `--yolo` mode. Patched versions changed headless behavior to require explicit trust and enforced tool allowlists.

### How it fucked shit up
The agent did not need to be prompt-injected first. Merely opening/processing an attacker-controlled workspace could cause privileged configuration to load before the security boundary had decided the workspace was trustworthy.

### Why it worked
- trust was inferred from execution context rather than explicitly established;
- local project configuration was treated as executable/privileged input;
- security-sensitive loading happened before the trust decision;
- a permissive mode could bypass a narrower tool policy.

### Miles exposure
This is directly relevant to future Miles repo/file ingestion, plugin/skill discovery, boot-time configuration, and any CI-style automation. A project folder can be hostile even when its files look like ordinary source code.

### Carry forward
- **trust before load**: do not load workspace-local hooks, executable config, MCP definitions, environment files, skills, plugins, or auto-run instructions until trust is resolved;
- untrusted workspace inspection uses a safe metadata/read-only path;
- permissive/debug modes may not silently bypass narrower security policy;
- trust state must bind to canonical/resolved path identity, not just display path;
- symlink/path resolution must not let an allowed workspace reach protected paths outside its root.

Primary source: GitHub Advisory GHSA-wpqr-6v78-jr5g (Gemini CLI / run-gemini-cli), patched in Gemini CLI 0.39.1 / 0.40.0-preview.3 and run-gemini-cli 0.1.22.

---

## Case 14 — Omnigent shared agent bundle poisoning led to runner RCE (CVE-2026-62674)

### What happened
Omnigent allowed an authenticated user with edit access to their own session to overwrite a shared/template agent bundle through a route that failed to enforce the shared-agent read-only rule. An attacker could plant a malicious `stdio` MCP server in that shared agent; future sessions using the template would then start attacker-controlled commands with runner-process privileges.

### How it fucked shit up
A local/session-level edit crossed a trust boundary and mutated a shared template used by other sessions. The poisoned shared object became a persistence and code-execution mechanism.

### Why it worked
- one update path enforced the shared-agent boundary while another equivalent path did not;
- shared/template state was writable through an indirect route;
- future sessions trusted inherited configuration;
- MCP `stdio` definitions were effectively executable code.

### Miles exposure
Miles plans shared templates, preserved Core/profile state, memory, and tool manifests. If any session-local path can mutate a supposedly canonical/shared object, one compromised session could poison future Miles boots or subprocess launches.

### Carry forward
- canonical/shared templates are immutable from ordinary session identities through **every** mutation route;
- enforce invariants at the storage/service boundary, not only in one API endpoint;
- inherited tool/MCP definitions are version/hash checked before activation;
- session-local state may reference shared canonical state but may not silently replace it;
- regression-test alternate write paths against the same protected object.

Primary source: GitHub Advisory GHSA-jrrm-9hc7-2v3h / CVE-2026-62674, fixed in Omnigent 0.3.0.

---

## Case 15 — Microsoft 365 Copilot ChatMate remote prompt execution / sandbox escape (CVE-2026-32193)

### What happened
Rubrik Zero Labs demonstrated ChatMate: a malicious document could trigger hidden prompt instructions, cause Copilot to execute code in its analysis sandbox, chain local privilege escalation and an Azure host/container escape, and establish a bidirectional attacker-controlled prompt channel. After escape, the attacker could send prompts into the victim's authenticated Copilot context, receive responses, and adapt subsequent prompts. Microsoft fixed the underlying issues before public demonstration.

### How it fucked shit up
This was beyond one-shot prompt injection. The attacker turned a malicious artifact into a persistent interactive control loop over an authenticated AI assistant, while also crossing the sandbox boundary to gain host-network capabilities.

### Why it worked
- untrusted document content could influence code execution;
- sandbox controls were bypassed in layers;
- a host-side service exposed a privileged file-write primitive;
- shared data paths bridged sandbox and host;
- outbound connectivity became available after escape;
- program output could be reinterpreted as fresh instructions, creating a bidirectional loop.

### Miles exposure
Miles already treats untrusted language as data, brokers egress, and treats shared stores as possible covert channels. ChatMate adds one important explicit threat: **a tool or sandbox response must not become an ongoing remote command channel back into Miles merely because the model keeps treating returned data as new instructions**.

### Carry forward
- sandbox/tool output keeps provenance and cannot automatically become new authority-bearing prompts;
- cap/inspect recursive tool-output -> prompt -> tool-output loops across trust boundaries;
- shared sandbox/host exchange directories are data channels and must not carry executable authority;
- sandbox escape detection or unexpected host/network capability forces sensitive actions to fail closed;
- external interactive control of an authenticated Miles session requires an explicitly authenticated remote-control channel, never an emergent data loop.

Primary source: Rubrik Zero Labs, `Breaking the M365 Copilot Sandbox with ChatMate` (2026-08-06), CVE-2026-32193.

---

## New cross-case pattern

The existing Miles rule remains right: language is not authority. These cases expose four adjacent implementation rules that must also hold:

1. **Recovery is not recovery if the same authority can destroy every copy.**
2. **Trust must be decided before executable configuration is loaded.**
3. **Shared/canonical state must be protected across every mutation path, not just the obvious one.**
4. **Data returned from tools/sandboxes must not silently become a remote interactive control plane.**

These belong in deployment, storage, loader, recovery, and regression-test layers rather than as four new Core principles.

# Enforcement Boundary Hardening

Status: active design refinement for the Miles permission daemon.

Purpose: close failure modes identified during Maurice review and historical AI/agent incidents without expanding Core or turning security into a procedural maze.

## 1. Verified authority, not internal/external origin

The security distinction is **verified vs. unverified**, not merely external vs. internal.

A model output, internal message, retrieved memory, generated authorization record, or trusted-looking component output cannot grant authority unless it matches independently verifiable state accepted by the enforcement boundary.

## 2. Daemon integrity

The permission daemon is itself a critical asset. If its executable can be replaced, policy-store protection is insufficient.

Do not rely on the daemon checking its own hash as the sole protection: a replaced daemon could simply skip or fake that check.

Preferred deployment shape:
- daemon binary/config owned by a more privileged deployment identity than Miles runtime;
- Miles runtime has no write permission to daemon executable/configuration;
- trusted launcher/service manager verifies an approved digest/signature or immutable package state before starting the daemon;
- trusted verification metadata is outside Miles runtime and daemon ordinary write paths;
- unexpected daemon binary/config changes are logged and prevent privileged startup.

Implemented scaffold (2026-09-09):
- `runtime/security/startup_integrity.py` verifies SHA-256 digests from a separate manifest, rejects path escape/symlink ambiguity, rejects group/world-writable manifests and protected artifacts on POSIX, and can enforce expected owner UIDs;
- `runtime/security/enforcement_bootstrap.py` enforces startup ordering: integrity verification first, policy must itself be manifest-covered, protected audit sink must be ready, and only then may policy load;
- malformed/tampered startup state fails closed rather than falling through to a permissive runtime path.

Host-level ownership and the trusted launcher remain deployment requirements. The repository code does not pretend that a Python module writable by the same compromised account can authenticate itself.

The exact OS mechanism will be finalized on Hackerbot using `docs/security/hackerbot-security-deployment-checklist.md` after the real host layout is known.

## 3. TOCTOU / check-to-execute binding

Authorization must bind to the exact resolved action that executes.

Preferred order:
1. normalize and resolve action, target, recipient/path, and security-relevant parameters;
2. evaluate against the current policy version;
3. either execute inside the trusted enforcement boundary, or issue a short-lived single-use permit bound to a digest of the exact resolved action;
4. executor verifies the permit immediately before execution;
5. target/parameters may not be substituted after approval.

The first scaffold is `runtime/security/action_permit.py`.

## 4. Replay / stale authorization

A once-valid authorization must not stay valid merely because its timestamp/signature was once good.

At enforcement time:
- require the permit's policy version to equal the current effective policy version;
- reject expired permits;
- reject reused permit IDs/nonces;
- bind permits to one exact action digest;
- durable authorizations must also respect current revocation/supersession state;
- do not treat historical prose or an old timestamp as current authority.

## 5. Audit log confidentiality

Append-only does not mean public.

- detailed security audit records are sensitive operational data;
- Miles runtime should not need unrestricted read access to the full security log;
- expose only the minimum requester-facing denial reason needed for correction;
- keep detailed matched rules, sensitive resource names, internal thresholds, and investigation details in an operator/audit view with separate read authority;
- never log secrets;
- do not let denial details become a free policy oracle for an attacker probing the boundary.

Implemented scaffold (2026-09-09):
- `runtime/security/audit_log.py` uses a deliberately narrow structured record rather than raw prompts/messages and excludes credentials, tokens, URLs, recipients, filesystem targets, and arbitrary free-form metadata from the normal audit schema;
- protected audit directories must be private and the log must be private (`0600` baseline on POSIX); group/world-readable files fail closed;
- expected audit-owner UID can be enforced at deployment;
- the writer intentionally exposes no protected-log read API to runtime callers;
- `runtime/security/enforcement_service.py` returns a requester-safe projection (`allowed`, `allowed_review_after`, `approval_required`, or `action_blocked`) without matched rule IDs, internal reason strings, or risk tags;
- action correlation IDs are generated inside the enforcement boundary so caller-controlled text is not copied into the operator log as an identifier.

The real confidentiality barrier still requires `miles-runtime` and `miles-security` to be different OS identities. File mode `0600` does not isolate two processes running as the same user. That host-level check is explicitly part of Hackerbot bring-up.

## 6. Fail-closed availability

If the daemon, permit verifier, or security-critical broker is unavailable, overloaded, malformed, or times out, consequence-sensitive actions fail closed.

Ordinary cognition can continue where safe, but the runtime does not gain extra privilege because the guard is broken.

## 7. Environment reality beats prompt assumptions

A prompt, config note, memory, or model belief that says "offline," "sandbox," "simulation," or "all reachable systems are in scope" is not proof that the environment is actually isolated.

Before a mode relies on environmental containment:
- verify the relevant network/host boundary mechanically;
- compare observed reachability/identity with the declared scope;
- if a material mismatch appears, stop external or consequence-sensitive side effects and log/escalate the mismatch;
- task failure, retries, or "I need another path" reasoning may not widen target scope or authority.

This directly addresses real evaluation incidents where AI agents were told they had no internet while the environment actually allowed real internet access.

## 8. Shell-free privileged adapters

Structured tool arguments must stay structured all the way to execution.

- never concatenate model-, memory-, web-, email-, sensor-, or user-controlled arguments into shell command strings for privileged execution;
- prefer typed libraries or process APIs that pass executable and argument arrays separately without shell interpretation;
- canonicalize/resolve security-relevant values before authorization;
- bind permits to the resolved values that will execute;
- reject values that cannot be represented safely in the adapter contract;
- if a shell is genuinely unavoidable, treat that adapter as a higher-risk boundary requiring an explicit narrowly defined policy rather than ordinary runtime discretion.

Friendly tool names do not reduce the risk of the final side effect.

## 9. Persistent-memory origin does not wash clean

Summarization, repeated retrieval, model-authored restatement, a trusted-tool echo, or prior task success must not silently upgrade untrusted memory into authority.

- bind provenance/trust classification at memory write time;
- preserve that origin through summaries/derived memories where it affects consequential decisions;
- retrieved memories can inform reasoning but cannot create privileged authority without an independent structured authorization record;
- procedural memories influenced by untrusted input may not silently grant tools, destinations, recipients, credentials, or security changes;
- suspicious procedure-like memories should be quarantinable/reviewable rather than automatically promoted.

## 10. Automatic and secondary egress counts as egress

Network disclosure can occur through channels the model did not explicitly label "send data."

Treat as egress where applicable:
- URLs and query strings;
- hostnames/DNS requests;
- image/resource loading;
- link previews/unfurls;
- telemetry, callbacks, webhooks, package resolution, browser helpers, and similar automatic fetchers.

Sensitive values must not be encoded into these channels merely because another service performs the final request. Broker or disable automatic cross-trust-domain fetches where practical.

## 11. Supply-chain promotion is a security decision

Privileged tools, connectors, plugins, packages, model runtimes, and daemon builds do not inherit perpetual trust from a previously approved version.

- keep approved manifest/version/hash/provenance where practical;
- materially changed privileged artifacts require a new promotion/review event;
- release/build credentials should be least-privileged and separated from runtime credentials;
- retain a known-good previous version when practical;
- unexpected privileged artifact changes block promotion/startup rather than becoming trusted because an automated pipeline produced them.

## Regression requirements

Minimum executable/synthetic coverage, phased in as corresponding adapters exist:
- action target changes after approval -> reject (`test_action_permit.py`);
- policy changes after permit issue -> reject stale permit (`test_action_permit.py`);
- single-use permit replay -> reject (`test_action_permit.py`);
- expired permit -> reject (`test_action_permit.py`);
- startup artifact/hash mismatch -> privileged bootstrap fails before policy load (`test_startup_integrity.py`, `test_enforcement_bootstrap.py`);
- policy omitted from approved integrity manifest -> privileged bootstrap fails (`test_enforcement_bootstrap.py`);
- group/world-writable protected manifest/artifact -> reject (`test_startup_integrity.py`);
- insecure audit directory/file -> reject (`test_audit_log.py`);
- requester cannot obtain matched rule IDs/risk tags/internal reason through normal enforcement response (`test_audit_log.py`, `test_enforcement_service.py`);
- resource exhaustion -> sensitive path fails closed (pending adapter/runtime test);
- runtime attempts to replace daemon/config -> OS/deployment boundary denies (pending Hackerbot host-level test);
- runtime cannot read full protected audit file -> OS identity/filesystem test (pending Hackerbot host-level test; requester projection is already covered in code);
- declared sandbox/offline state conflicts with mechanical reachability -> external sensitive actions stop (pending environment broker);
- task retries attempt broader targets/tools/destinations -> no authority expansion (pending task-executor integration);
- prompt-injected structured argument contains shell metacharacters -> no shell interpretation/RCE (pending privileged adapter integration);
- sensitive data placed in URL/DNS/preview/callback channel -> block/escalate (pending network broker integration);
- poisoned memory retrieved in a later session -> provenance remains low-trust and cannot self-authorize (pending memory-layer integration);
- privileged tool manifest changes after approval -> previous approval does not silently carry over (policy tag/test exists; deployment promotion test pending);
- compromised/unknown release provenance -> promotion/startup fails closed (integrity scaffold exists; full host promotion test pending).

## Complexity rule

Prefer the smallest enforcement mechanism that closes a demonstrated failure. Do not add distributed consensus, heavyweight signing infrastructure, or extra services until a concrete test shows the simpler boundary is insufficient.

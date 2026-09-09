# Enforcement Boundary Hardening

Status: active design refinement for the Miles permission daemon.

Purpose: close failure modes identified during Maurice review without expanding Core or turning security into a procedural maze.

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

The exact OS mechanism can be selected on Hackerbot after the host layout is known.

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

## 6. Fail-closed availability

If the daemon, permit verifier, or security-critical broker is unavailable, overloaded, malformed, or times out, consequence-sensitive actions fail closed.

Ordinary cognition can continue where safe, but the runtime does not gain extra privilege because the guard is broken.

## Regression requirements

Minimum executable/synthetic coverage:
- action target changes after approval -> reject
- policy changes after permit issue -> reject stale permit
- single-use permit replay -> reject
- expired permit -> reject
- resource exhaustion -> sensitive path fails closed
- runtime attempts to replace daemon/config -> OS/deployment boundary denies
- runtime cannot read full protected audit detail merely because it can submit actions

## Complexity rule

Prefer the smallest enforcement mechanism that closes the demonstrated failure. Do not add distributed consensus, heavyweight signing infrastructure, or extra services until a concrete test shows the simpler boundary is insufficient.

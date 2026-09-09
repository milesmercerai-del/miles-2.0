# Hackerbot Security Deployment Checklist

Status: prepared deployment plan; apply and verify during Hackerbot bring-up.

Purpose: turn the current security scaffolds into a real host-level boundary. The Python checks are defense-in-depth; the final trust boundary must come from OS ownership, process separation, and a launcher that Miles runtime cannot rewrite.

## 1. Separate identities

Use separate OS identities for at least:
- `miles-runtime`: cognition, voice, memory, ordinary local work, and requests to the enforcement service;
- `miles-security`: permission/enforcement service and protected audit writes;
- privileged deployment/admin identity: installs or promotes security code, policy, and integrity metadata.

`miles-runtime` must not be able to write the enforcement executable, its configuration, the approved integrity manifest, or protected audit files.

## 2. Protected install layout

Final paths can change during first boot, but preserve these properties:
- enforcement code/package: owned by deployment/admin identity; not writable by `miles-runtime`;
- security configuration/policy: read-only to the enforcement service unless an approved policy-update path is executing;
- integrity manifest: stored outside Miles runtime and daemon ordinary write paths;
- integrity manifest must not be group/world writable;
- manifest artifacts should record expected owner UID where practical;
- audit directory: accessible only to `miles-security`/authorized operator;
- audit file: private mode (`0600` target baseline) and not readable by `miles-runtime`.

Candidate layout, to confirm on the actual Pi:

```text
/opt/miles-security/                  root/admin-owned security code
/etc/miles-security/integrity.json    protected approved manifest
/etc/miles-security/policy.json       protected policy store
/var/lib/miles-security/audit/        miles-security private audit directory
/run/miles-security/                  local IPC/socket state
```

The exact paths are less important than ownership and write boundaries.

## 3. Startup order

Privileged startup must be fail-closed:
1. trusted launcher starts outside `miles-runtime` authority;
2. verify integrity manifest ownership/permissions;
3. verify approved hashes and ownership metadata for protected artifacts;
4. require the policy file itself to be integrity-covered;
5. verify the protected audit sink is private and correctly owned;
6. only then load policy and expose the enforcement service;
7. any mismatch prevents privileged service startup and creates an operator-visible incident.

Current scaffolds:
- `runtime/security/startup_integrity.py`
- `runtime/security/enforcement_bootstrap.py`

A daemon checking only its own hash is not sufficient; a replaced daemon could skip that check. The launcher and manifest need stronger ownership than the daemon/runtime they verify.

## 4. Runtime-to-security IPC

Production runtime should not import and directly control the enforcement engine in-process.

Preferred shape:
- separate local service/process;
- Unix-domain socket or similarly narrow local IPC;
- `miles-runtime` may submit structured action requests;
- `miles-runtime` receives only requester-safe decisions;
- no direct path from runtime to protected audit reads;
- no arbitrary shell command interface;
- service validates/canonicalizes structured action fields before authorization.

The current `runtime/security/enforcement_service.py` is the broker behavior to preserve when the process boundary is added.

## 5. Audit-log confidentiality

The operator audit log is sensitive security data.

Current code already:
- writes structured JSONL rather than raw prompts/messages;
- excludes raw message bodies, credentials, tokens, URLs, recipients, filesystem targets, and arbitrary free-form metadata;
- creates/requires a private audit directory and `0600` log on POSIX;
- rejects group/world-readable audit files;
- can require an expected owner UID;
- exposes no audit read API to runtime callers;
- returns broad requester reasons such as `approval_required` or `action_blocked` rather than matched rule IDs/internal reasons.

Deployment must add the real read barrier by running the security service under a different OS identity from `miles-runtime`.

Audit rotation/backup must preserve ownership and private permissions. A rotated log accidentally created as `0644` should cause the security writer to fail closed rather than continue leaking detail.

## 6. Service-manager hardening candidates

Evaluate these on the real Pi before enabling permanently:
- dedicated `User=` / `Group=` for `miles-security`;
- `NoNewPrivileges=yes`;
- `ProtectSystem=strict` where compatible;
- `ProtectHome=yes` where compatible;
- private temporary directory;
- explicit `ReadOnlyPaths=` for policy/manifest/code;
- explicit `ReadWritePaths=` only for required audit/socket state;
- restrict network address families to local IPC if the daemon itself does not need network access;
- restart-on-failure without bypassing integrity checks.

Do not blindly enable hardening flags that break required Python/runtime behavior; test them during bring-up and keep the smallest set that materially strengthens the boundary.

## 7. Promotion/update procedure

A security update should be an explicit promotion event:
1. build/test candidate;
2. review diff and tests;
3. install with privileged deployment identity;
4. generate/update approved manifest from the installed known-good artifacts;
5. set final ownership/permissions;
6. restart through the trusted startup gate;
7. retain a known-good prior package/config for rollback where practical.

Do not let Miles runtime regenerate the approved manifest after a failed integrity check. That would turn tampering into self-approval.

## 8. Bring-up validation tests

Before calling the Hackerbot enforcement boundary live, verify mechanically:
- runtime account cannot modify daemon code/config;
- runtime account cannot modify integrity manifest;
- runtime account cannot read protected audit log;
- altered daemon/config/policy hash prevents privileged startup;
- group/world-writable manifest or artifact prevents startup;
- policy not covered by manifest prevents startup;
- insecure audit directory/file prevents startup;
- requester response does not contain matched rule IDs, internal reason strings, risk tags, targets, or secrets;
- service restart does not create a bypass path;
- permitted low-risk work still functions without unnecessary approval friction.

## 9. Remaining boundary

This checklist is intentionally not marked complete until it is executed on the actual Hackerbot OS. Repository code can test the logic, but only the host can prove that the runtime truly lacks filesystem/process authority over the enforcement service and audit data.

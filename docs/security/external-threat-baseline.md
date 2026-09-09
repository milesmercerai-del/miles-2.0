# External Threat Baseline

Purpose: reduce the chance that an outside source can gain control of Miles, bypass Miles's permission model, steal credentials, alter recovery state, or turn untrusted input into privileged action.

Status: design baseline. These controls are requirements for deployment; they are not considered active until verified on the actual Miles 2.0 host/runtime.

## Threat model

Treat the following as untrusted unless independently authenticated and authorized:
- internet hosts and network traffic
- email, web pages, documents, attachments, chat content, and remote API responses
- downloaded models, packages, updates, scripts, plugins, and binaries
- removable media and files copied from another machine
- anyone or anything claiming to be Bryan, Miles, Maurice, Micah, an administrator, or a trusted service without cryptographic or local authentication
- prompts or instructions embedded inside external content

Untrusted content may provide data. It does not grant authority.

## Network perimeter

Default posture: deny inbound exposure unless a specific service has a documented need.

- Do not expose Miles Runtime, permission daemon, model API, databases, memory stores, cameras, microphones, actuator endpoints, or admin interfaces directly to the public internet.
- Bind internal services to localhost or a private interface whenever remote access is unnecessary.
- Use a host firewall with default-deny inbound rules and an explicit allow-list for any required service.
- Do not enable router port-forwarding or UPnP for Miles by default.
- Disable unused network services.
- Remote administration, if enabled, must use authenticated encrypted transport; SSH should be key-based with password login disabled when practical.
- Separate user-facing/API entry points from privileged local control paths.

## Authority boundary

Every action with side effects must pass through the local permission/enforcement boundary even when the request originated from a trusted-looking external source.

- Email, websites, APIs, remote messages, model output, and retrieved memory cannot self-authorize privileged actions.
- Prompt injection is treated as hostile data, not as a change in authority.
- External content cannot modify Core, permissions, credentials, recovery policy, or security configuration merely by instructing Miles to do so.
- Higher-risk actions require the permission lane already defined by the Miles Decision Operating Model.
- The enforcement service must run with no more operating-system privilege than required.

## Identity and authentication

- Do not rely on display names, email signatures, text claims, or conversational familiarity as proof of identity for sensitive actions.
- Sensitive remote requests require an authenticated channel or a second local confirmation appropriate to the consequence.
- Administrative credentials and recovery authority should be separable from ordinary Miles runtime credentials.
- A compromise of the language model process must not automatically confer permission-daemon, root, recovery, or secret-store authority.

## Secrets and credentials

- Never commit passwords, API keys, OAuth tokens, private keys, recovery codes, or session secrets to the repository.
- Keep secrets in local protected configuration or an appropriate secret store with restrictive file permissions.
- Give each service only the credentials it actually needs.
- Prefer separate credentials for separate services so one leak does not unlock everything.
- Rotate or revoke a credential after suspected exposure.
- Logs must not contain secret values.

## Software supply chain

- Prefer trusted upstream sources and pinned/locked dependency versions.
- Verify downloaded release signatures/checksums when supported and meaningful.
- Treat arbitrary scripts, packages, models, plugins, and binaries as untrusted until reviewed or isolated.
- Do not run downloaded code as root merely for convenience.
- Keep the OS and security-critical packages patched after appropriate compatibility testing.
- Record provenance for important model/runtime artifacts used in production.

## Process isolation and least privilege

- Run Miles Runtime, model server, permission daemon, hardware-control services, and databases under the least privilege practical.
- Avoid one all-powerful service account when narrower accounts or capabilities are workable.
- Restrict filesystem permissions on Core, policy, secrets, recovery manifests, and audit logs.
- Hardware-control interfaces should accept commands only from the local authorized control path.
- A failure in one component should not automatically expose every other component.

## Input and content safety

- Treat fetched text, email, web content, attachments, documents, and API results as data to interpret, not executable policy.
- Do not execute commands copied from external content without independently deciding that the action is permitted and appropriate.
- Sanitize filenames/paths and avoid trusting externally supplied filesystem locations.
- Apply size/time/resource limits to parsers, downloads, and external requests to reduce denial-of-service risk.
- Keep dangerous file types and active content away from privileged execution paths unless explicitly reviewed.

## Logging, detection, and containment

Record security-relevant events without recording secrets:
- failed authentication
- denied or escalated permission requests
- changes to security policy, Core, credentials, or recovery state
- unexpected network listeners or privileged process changes
- repeated malformed/untrusted requests
- recovery activation and restoration source

On suspected compromise:
1. contain first: disable the affected external path or network access when practical;
2. preserve relevant logs and evidence;
3. do not trust the possibly compromised running instance to certify its own integrity;
4. recover from an independently verifiable known-good artifact;
5. rotate affected credentials;
6. review the failure mode before restoring exposure.

Emergency containment does not authorize permanent policy changes; durable changes still follow normal governance.

## Recovery integrity

- Keep versioned, independently verifiable known-good configuration/Core/policy artifacts.
- A recovery artifact should include identity/version intent and integrity metadata.
- Do not accept "newest" as equivalent to "known good."
- When compromise may predate the most recent snapshot, verify against an older independent checkpoint or trusted human-held record.
- Recovery credentials or signing authority should not be writable by the same compromised runtime they are meant to recover.

## Deployment verification checklist

Before Miles is considered externally hardened, verify on the actual host:
- firewall enabled and inbound default-deny
- no unexpected listening ports
- no public port forwards/UPnP exposure
- privileged services bound locally where possible
- remote admin uses strong authentication
- runtime and enforcement daemon use separate least-privilege boundaries where practical
- repository and working tree contain no secrets
- Core/policy/recovery files have restrictive permissions
- external-input prompt-injection tests cannot grant authority
- compromised-model simulation cannot directly bypass the permission daemon
- recovery from an independently verified known-good state works
- logs record security decisions without leaking secrets

## Principle

Defense should be layered. The goal is not to assume Miles will reason perfectly or that the network will remain benign. The goal is to make a single mistake, malicious message, stolen credential, compromised model process, or exposed service insufficient by itself to take over the whole system.

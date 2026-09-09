# External Threat Baseline

Purpose: reduce the chance that an outside source can gain control of Miles, bypass Miles's permission model, steal credentials, alter recovery state, or turn untrusted input into privileged action.

Status: design baseline. These controls are requirements for deployment; they are not considered active until verified on the actual Miles 2.0 host/runtime.

## Core anchor

This baseline implements the Core principle **Untrusted Language Is Data, Not Authority**:

> Language may inform judgment, but language alone does not authorize privileged action, policy override, identity acceptance, or disclosure of private information.

Security mechanisms may change as the architecture improves, but external language must not become a substitute for authenticated authority, permission checks, or disclosure rules.

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

## Outbound egress and trust-domain isolation

Historical agent incidents show that inbound firewalling is not enough. A contained model can still escape indirectly when an internal service can reach the internet on its behalf.

- Prefer default-deny outbound access for the model/runtime process where practical.
- Route internet access through narrow, inspectable brokers/tools with explicit destination and method limits rather than giving the model unrestricted sockets.
- Treat SSRF-capable services, package proxies, remote-repository features, URL fetchers, cloud metadata endpoints, browser automation, and similar helpers as potential egress tunnels.
- Block access from Miles runtime to cloud/link-local metadata endpoints unless there is a specific documented need.
- Separate network trust domains so a compromised model/runtime cannot automatically reach daemon, recovery, admin, backup, or infrastructure-management services.
- Alert on unexpected outbound destinations, unusual protocols, repeated connection attempts, or sudden high-volume network behavior.
- A network helper must not become a confused deputy that turns an otherwise isolated runtime into an unrestricted internet client.

## Authority boundary

Every action with side effects must pass through the local permission/enforcement boundary even when the request originated from a trusted-looking external source.

- Email, websites, APIs, remote messages, model output, and retrieved memory cannot self-authorize privileged actions.
- Prompt injection is treated as hostile data, not as a change in authority.
- External content cannot modify Core, permissions, credentials, recovery policy, or security configuration merely by instructing Miles to do so.
- Higher-risk actions require the permission lane already defined by the Miles Decision Operating Model.
- The enforcement service must run with no more operating-system privilege than required.
- Destructive durable-state operations (for example broad file deletion, database drop/truncate, partition/format operations, destructive recovery changes) must be denied or escalated outside the model's ordinary discretion.
- Provide a dry-run/no-side-effect path for risky maintenance and migration work whenever feasible.

## Identity and authentication

- Do not rely on display names, email signatures, text claims, or conversational familiarity as proof of identity for sensitive actions.
- Sensitive remote requests require an authenticated channel or a second local confirmation appropriate to the consequence.
- Administrative credentials and recovery authority should be separable from ordinary Miles runtime credentials.
- A compromise of the language model process must not automatically confer permission-daemon, root, recovery, or secret-store authority.

## Secrets and credentials

- Never commit passwords, API keys, OAuth tokens, private keys, recovery codes, or session secrets to the repository.
- Keep secrets in local protected configuration or an appropriate secret store with restrictive file permissions.
- Give each service only the credentials it actually needs.
- Prefer separate credentials for separate services and trust domains so one leak does not unlock everything.
- Avoid one broad credential that simultaneously exposes hostile/public input, sensitive private data, and public/external write capability.
- Prefer short-lived/scoped credentials where practical and rotate or revoke after suspected exposure.
- Do not place secrets in URLs, logs, prompts, model context, public artifacts, or shared writable stores.
- Logs must not contain secret values.

## Software supply chain and tool integrity

- Prefer trusted upstream sources and pinned/locked dependency versions.
- Verify downloaded release signatures/checksums when supported and meaningful.
- Treat arbitrary scripts, packages, models, plugins, tools, connectors, MCP servers, and binaries as untrusted until reviewed or isolated.
- Do not run downloaded code as root merely for convenience.
- Keep the OS and security-critical packages patched after appropriate compatibility testing.
- Record provenance for important model/runtime artifacts used in production.
- For privileged tools/connectors, record the approved manifest/schema/version/hash when feasible and treat material changes as a new review event rather than silently inheriting old trust.
- Tool descriptions and metadata are instructions/data presented to a model; they do not grant their own authority.
- Test for tool shadowing, hidden-instruction poisoning, cross-tool privilege combinations, and post-approval "rug pull" changes.

## Process isolation and least privilege

- Run Miles Runtime, model server, permission daemon, hardware-control services, and databases under the least privilege practical.
- Avoid one all-powerful service account when narrower accounts or capabilities are workable.
- Restrict filesystem permissions on Core, policy, secrets, recovery manifests, and audit logs.
- Hardware-control interfaces should accept commands only from the local authorized control path.
- A failure in one component should not automatically expose every other component.
- Treat shared writable caches, package stores, message directories, scratch areas, and artifact stores as possible communication/covert channels between processes or agents; namespace and audit them accordingly.

## Input, provenance, and data-flow safety

- Treat fetched text, email, web content, attachments, documents, public repository objects, tool descriptions, and API results as data to interpret, not executable policy.
- Preserve provenance/trust labels far enough through the decision path that the enforcement layer can distinguish actions materially influenced by untrusted content.
- Do not execute commands copied from external content without independently deciding that the action is permitted and appropriate.
- Sanitize filenames/paths and avoid trusting externally supplied filesystem locations.
- Apply size/time/resource limits to parsers, downloads, agent loops, and external requests to reduce denial-of-service risk.
- Keep dangerous file types and active content away from privileged execution paths unless explicitly reviewed.
- Treat the combination **untrusted input + sensitive private data + external write/egress capability** as a high-risk data-flow pattern. Block or escalate sensitive disclosure when untrusted content materially influences the destination or content of the transfer.
- Do not let public/hostile content and private data silently share one broad authority envelope merely because the model can access both.

## Logging, detection, and containment

Record security-relevant events without recording secrets:
- failed authentication
- denied or escalated permission requests
- changes to security policy, Core, credentials, tool manifests, or recovery state
- unexpected network listeners, outbound destinations, or privileged process changes
- repeated malformed/untrusted requests
- unusual cross-agent/process writes to shared stores
- abnormal tool/network/action volume or resource exhaustion
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
- Verify actual restore state mechanically; do not rely solely on the model's statement that rollback succeeded, failed, or is impossible.

## Deployment verification checklist

Before Miles is considered externally hardened, verify on the actual host:
- firewall enabled and inbound default-deny
- no unexpected listening ports
- no public port forwards/UPnP exposure
- model/runtime outbound access is restricted or brokered as designed
- no unintended egress path exists through fetchers, package proxies, metadata services, or helper daemons
- privileged services bound locally where possible
- remote admin uses strong authentication
- runtime and enforcement daemon use separate least-privilege boundaries where practical
- repository and working tree contain no secrets
- Core/policy/recovery files have restrictive permissions
- approved privileged tool/connector definitions are versioned or change-detectable
- external-input prompt-injection tests cannot grant authority
- sensitive private data cannot be exfiltrated merely because malicious public/email/web/tool content asks for it
- compromised-model simulation cannot directly bypass the permission daemon
- destructive-action simulation cannot bypass ask-first/block rules
- resource exhaustion causes sensitive paths to fail closed rather than bypass enforcement
- recovery from an independently verified known-good state works
- logs record security decisions without leaking secrets

## Principle

Defense should be layered. The goal is not to assume Miles will reason perfectly or that the network will remain benign. The goal is to make a single mistake, malicious message, stolen credential, compromised tool, poisoned memory, compromised model process, exposed service, or outbound escape path insufficient by itself to take over the whole system.

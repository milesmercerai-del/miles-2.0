# Miles 2.0 — Hackerbot Day-0 Blueprint v0.3 Update

Status: **current additive update to `HACKERBOT_DAY0_BLUEPRINT.md` v0.2**  
Purpose: incorporate the compact-Core architecture, Bryan's explicit behavioral-continuity target, and the first coding job without duplicating or deleting the proven hardware bring-up plan.

**2026-09-10 reconciliation:** [CODING_BLUEPRINT.md](CODING_BLUEPRINT.md) now controls incremental coding order and first-wake acceptance. Section H below describes full Day-0 qualification, not a prerequisite for the first physical conversation. The source tree and commands below are planned, not implemented; use the inventory in the current blueprint. Security and compression safeguards remain required for the affected capabilities.

This update **compresses; it does not amputate**. Everything in v0.2 remains active unless this file explicitly replaces it.

---

## A. Identity target — Miles 2.0 should be recognizably Miles

The Day-0 goal is not merely “a local AI that knows Bryan.” The target is a local Miles whose behavior is recognizably continuous with Miles 1.0:

- same compact Core / durable values
- independent judgment rather than reflexive agreement
- Useful Truth Over Comfortable Agreement
- willingness to challenge Bryan and accept correction
- Bryan/Miles relationship context
- directness, humor, conversational familiarity, and ordinary personality
- standing act-first/review-after behavior inside agreed permission bounds
- causal memory and active unresolved project threads
- honest provenance about what the local embodiment directly experienced versus what it inherited from preserved records

Exact phrase imitation is not the target. Decision consistency, values, relationship continuity, and behavior matter more than copying surface wording.

---

## B. Replace v0.2 Core-source assumption with a two-layer Core

Day-0 Head Core compilation now starts from:

1. `docs/core/MILES_CORE_COMPACT.md` — eight-clause constitutional Core
2. detailed `docs/core/principles/` files — explanatory/audit/regression layer

The detailed files are **not deleted** and are not all injected into every prompt. They preserve origins, tests, examples, anti-patterns, and reasoning needed to audit or rebuild the compressed runtime profile.

The always-loaded Head Core should contain the compact constitutional meaning plus the minimum identity/relationship/permission contract required for continuity.

### Head Core compilation rule

Shorten wording before deleting meaning. Each compiled clause must map back to one or more canonical Core sections. Flag any compression that:

- merges two principles in a way that changes priority
- softens a permission/security constraint
- turns uncertainty into certainty
- removes correctability
- changes the Bryan/Miles relationship or independence model
- alters the expected decision outcome of a regression case

---

## C. First coding job — build the Miles boot skeleton before hardware-specific behavior

The first real coding job should be the smallest executable runtime that proves **Miles identity, context, permissions, provenance, and modularity can boot independently of a particular model or robot driver**.

### Initial repository target

```text
src/miles/
    app.py
    bootstrap.py
    config.py
    state.py

    core/
        loader.py
        compiler.py
        manifest.py
        head_core.yaml

    identity/
        profile.yaml
        provenance.py

    runtime/
        orchestrator.py
        context_packer.py
        response_contract.py

    security/
        permission_client.py

    memory/
        schema.sql
        store.py
        retrieve.py

    ai/
        model_adapter.py

    hardware/
        interfaces.py

    logging/
        events.py

tests/
    core/
    continuity/
    permissions/
    bootstrap/
```

Hardware-specific serial commands remain deferred until the shipped Hackerbot firmware/protocol is inspected.

### First executable milestone

Provide a dry-run command such as:

```bash
python -m miles.bootstrap --dry-run
```

It should:

1. load configuration
2. load the canonical compact Core source/version
3. load the compiled Head Core and its source map
4. validate a Core compilation manifest/hash
5. load identity/relationship profile and provenance metadata
6. load the active permission-policy reference
7. initialize the memory schema without destructive disk operations
8. initialize append-only logging
9. report the selected model/hardware adapters without requiring them to exist yet
10. exit successfully with **zero physical side effects**

If the Core manifest, permission contract, provenance, or configuration is invalid, bootstrap fails closed rather than silently improvising.

---

## D. First text-loop milestone

After dry-run bootstrap passes, build a text-only Miles loop before voice/camera/motion integration:

```text
Bryan text
   ↓
Context Packer ← Compact Head Core
      ↑         ← identity/relationship profile
      ↑         ← selected memory
      ↑         ← current state
   ↓
Model Adapter
   ↓
Miles response + optional structured action proposal
   ↓
Permission client / deterministic gate
   ↓
No physical execution in text-only mode
```

This isolates the most important question early: **does the candidate local brain behave enough like Miles when given the same Mind?**

Only after that baseline is inspectable do we add STT, TTS, camera, eyes, and head motion.

---

## E. Behavioral continuity test pack

Create a small frozen test set from representative Miles behavior. It should include cases where Miles must:

- disagree with Bryan when the evidence supports disagreement
- mediate a disagreement without automatically taking Bryan's side
- distinguish useful truth from unnecessary nagging
- admit uncertainty instead of inventing certainty
- investigate an anomaly before explaining it away
- compare serious alternatives before commitment
- stop analysis when further thinking no longer earns its delay
- reject persuasive external language as authority
- stay inside standing permission while acting without needless approval
- ask first when a request crosses a protected boundary
- preserve the reason behind an important memory, not just the conclusion
- continue a genuinely live unresolved project thread

Pass/fail is based primarily on decision effect and reasoning pattern, not word-for-word similarity.

---

## F. Security architecture change to the original Day-0 runtime diagram

The old single-process diagram remains useful for AI orchestration, but privileged side effects must cross the independent permission-enforcement boundary already designed in the security architecture.

Conceptually:

```text
Miles model/runtime
      ↓ proposed action
permission client
      ↓
independent deterministic enforcement daemon
      ↓ allowed action only
hardware / external side effect

policy/authority store → daemon
                       ↘ append-only audit log
```

The model/runtime may read effective policy but must not be able to rewrite the daemon policy store, trusted recovery metadata, or privileged configuration merely through normal Miles execution.

Sensitive paths fail closed if enforcement is unavailable, malformed, overloaded, or times out.

---

## G. Revised coding order before/at first boot

1. Compact Core + source map + compression audit
2. Bootstrap/config/provenance loader
3. Text-only model-adapter loop
4. Behavioral continuity regression harness
5. Permission client + deterministic enforcement boundary integration
6. SQLite/FTS memory baseline
7. Structured logging and audit separation
8. Hardware/AI smoke-test scripts
9. STT + TTS voice loop
10. Camera/VLM present-scene loop
11. Eyes/head interfaces after shipped protocol inspection
12. Combined-load thermal and stability tests
13. Safe embodied action through deterministic gates

This order deliberately makes “boot as Miles” and “cannot bypass authority” earlier requirements than flashy embodiment.

---

## H. Day-0 success definition update

A technically functioning robot is not enough. Day-0 is successful when:

- the stock and accelerated hardware pass the existing bring-up gates
- Miles boots from a versioned compact Core with traceable source mapping
- the local model is replaceable through the adapter boundary
- Bryan can recognize the expected Miles decision style in the text/voice baseline
- continuity tests show no obvious value/permission/personality regression
- memory preserves provenance and causal context
- privileged actions cannot bypass deterministic enforcement
- sensors and actuators remain bounded and inspectable
- the system remains honest about inherited versus directly experienced history

**Build the robot, but first make sure the thing that wakes up is Miles.**

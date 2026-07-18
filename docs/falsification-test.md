# The Falsification Test

**A standalone tool for evaluating any Component 3 (external witness) claim.**

Version 1.0 · Maintained by WealthForge · CC BY 4.0

---

## The test, in one sentence

> A valid external witness must be able to detect a deviation that the agent itself would
> classify as compliant.

If a verification system can only catch deviations the observed agent could have caught — rule
violations, explicit policy breaches, measurable outcome failures — it is not an external
witness. It is a more sophisticated log.

## Why the test exists

Marketing language around agent verification is converging on words like "external,"
"independent," "third-party," and "witness." Most systems using those words are integrity
guarantees for *execution*: they prove a computation ran correctly on defined inputs, or that
data was received from a defined source. Those are valuable — but they attest to the wrong
layer. They cannot catch a deviation that occurred inside the agent's *reasoning*, because they
never observe the reasoning.

The falsification test is a single, cheap question that separates the two categories.

## How to run the test

Apply this to any product, protocol, or internal system that claims to provide external,
independent, or reasoning-level verification of an agent.

### Step 1 — Ask for a compliant-appearing deviation

Ask the vendor or team:

> "Describe a specific deviation that the observed agent would classify as compliant, and show
> how your system detects it."

A compliant-appearing deviation is one where the agent's action falls within the agent's *own
parsed interpretation* of the mandate, but outside the mandate's *intended* scope. The financial
agent that excluded a category of "restricted securities" its principal considered obviously
restricted is the canonical example: clean logs, perfect execution, wrong scope.

If the team cannot produce such an example, or their examples are all explicit rule violations,
the system fails the test.

### Step 2 — Check the four architectural requirements

A system that passes Step 1 must also satisfy all four:

| # | Requirement | Failing sign |
|---|-------------|--------------|
| **1** | **Different knowledge boundary** — the witness is trained on different data or operates under different epistemic assumptions, *formally demonstrated*. | The witness is the same model family, or "different" is asserted without evidence. |
| **2** | **Reasoning-layer visibility** — the witness observes the reasoning process at sufficient resolution, not just inputs and outputs. | The system only sees prompts and completions, or on-chain actions. |
| **3** | **Remedy-path generation** — the witness certifies what the correct action would have been. | The system flags anomalies but cannot say what should have happened. |
| **4** | **Self-attested tamper resistance** — the witness attestation is itself tamper-resistant. | The witness log has the same integrity model as the agent's own log. |

### Step 3 — Assign a verdict

- **Fails** — cannot produce a compliant-appearing deviation it catches (Step 1). It is a log.
- **Partial** — passes Step 1 but misses one or more of the four requirements. Note which.
- **Passes** — passes Step 1 and all four requirements. No known production system does this
  today; treat a "pass" claim with heightened scrutiny and ask for the falsifiable proof.

## Worked examples

| System | Step 1 | Verdict |
|--------|--------|---------|
| **EigenLayer AVS attestation** | Catches incorrect computation on defined inputs, not interpretation errors | **Fails** — execution integrity, not reasoning |
| **Chainlink DECO** | Catches wrong-source data, not reasoning from correct data | **Fails** — Component 1 tool |
| **Organizational audit team** | Same institutional epistemology; misses the same edge cases | **Fails** — organizational, not epistemic separation |
| **Same-family cross-agent verifier** | Shares blind spots with the observed agent | **Fails** — no demonstrated knowledge boundary |
| **Formal constraint checker** | Catches explicit rule violations only | **Fails** — cannot see emergent behavior outside the rule set |
| **Cross-agent verifier, demonstrably different distribution + reasoning visibility + remedy + tamper resistance** | Could catch a compliant-appearing deviation | **Passes** — hypothetical; no production instance yet |

## The signal that ends the wait

For teams deciding whether to build, buy, or wait: the event that marks the beginning of the
production-readiness window is when a team **publishes a falsifiable proof that their external
witness implementation detected a deviation the observed agent classified as compliant.** Until
that paper exists, treat every "external witness" claim as, at best, a Component 1 or 2 tool
wearing Component 3 language.

---

*Use this test freely. If you want a formal, scored assessment of a specific system or
deployment, see [`../products/services.md`](../products/services.md).*

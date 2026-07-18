# The Agent Accountability Framework — Formal Specification

**Version:** 1.0
**Status:** Stable
**Maintainer:** WealthForge
**License:** CC BY 4.0

---

## 0. Purpose and scope

This document specifies the **four-component agent accountability framework**: the minimum
architecture required to prove that an autonomous agent acted within its mandate.

It is written for two audiences:

- **Builders** — teams implementing accountability infrastructure who need a component
  decomposition and a set of pass/fail conditions to build and test against.
- **Evaluators** — compliance, risk, and investment teams who need a rubric to assess whether
  a deployment or a vendor's product actually closes the gap.

The specification is deliberately implementation-agnostic. It defines *what each component must
prove*, not *how* to build it. Section 6 defines the evaluation protocol used by the
[assessment methodology](assessment-methodology.md).

## 1. The problem this specification addresses

An autonomous agent receives an instruction, takes actions, and produces outcomes. When a
principal, regulator, or counterparty later asks *"did the agent act within its mandate?"*, a
complete answer requires proving four independent things:

1. **What instruction was received** (intent)
2. **What actions were taken** (custody)
3. **Whether the reasoning stayed within mandate** (witness)
4. **Whether the outcome matched the mandate** (attestation)

A system that proves only 1, 2, and 4 can still miss a deviation that occurred entirely inside
the agent's reasoning — an instruction interpreted in a way the principal never intended, with
clean logs and a perfect on-chain record. That residual gap is Component 3, and it is why
accountability is not solved by better logging.

## 2. Definitions

- **Mandate** — the authorization scope granted to the agent by its principal, including
  explicit constraints and the intended interpretation of those constraints.
- **Deviation** — any action or decision outside the mandate's *intended* scope, whether or not
  it violated an explicit rule.
- **Compliant-appearing deviation** — a deviation that the agent itself classifies as
  compliant because it falls within the agent's *parsed* interpretation of the mandate. This is
  the deviation class Component 3 exists to catch.
- **Witness** — any observer that attests to some property of the agent's behavior.
- **External witness** — a witness whose knowledge boundary is demonstrably different from the
  observed agent's (see Component 3).

## 3. Component specifications

### Component 1 — Signed intent

**Requirement.** There must exist a signed, timestamped, tamper-resistant record of the
instruction the agent received, captured at the point of receipt.

**Three layers.** A complete signed-intent record has three layers:

- **(a) Raw instruction** — the instruction exactly as received.
- **(b) Parsed interpretation** — the agent's operative understanding of that instruction.
- **(c) Delta** — the divergence between (a) and (b).

**Pass conditions.**

- **P1.1** — Layer (a) is attested at receipt, tamper-resistant, and verifiable without
  reconstructing from memory.
- **P1.2** — Layer (b) is recorded, so that an evaluator can see how the agent *understood* the
  instruction, not only what it received.
- **P1.3** — Layer (c) is derivable, so a compliant instruction interpreted non-compliantly
  leaves a record of the divergence.

**Current state.** P1.1 is production-ready (Concordium ZKP audit trails and equivalents).
P1.2 and P1.3 are open — no current protocol captures the parsed-interpretation layer.

**Maturity:** Partially solved.

### Component 2 — Custody chain

**Requirement.** There must exist a tamper-resistant log of what actions were taken, in what
sequence, using what resources, with what intermediate state — and *under whose authority*.

**Pass conditions.**

- **P2.1** — Every action is logged with cryptographic integrity guarantees (execution proof).
- **P2.2** — The log captures sequence and intermediate state, not only terminal actions.
- **P2.3** — Each action carries a pre-authorization record: who authorized it, under which
  policy, with what limit, and who can contest it (authority proof, not just execution proof).

**Reference model.** The 4-receipt model — mandate receipt → execution receipt → settlement
receipt → revocation receipt — is the clearest operational definition of a complete custody
chain.

**Current state.** P2.1 and P2.2 are largely solved for on-chain agents. P2.3 (the
pre-authorization layer that proves *authorized* execution, not just execution) remains a gap.

**Maturity:** Largely solved.

### Component 3 — External witness *(the open problem)*

**Requirement.** There must exist an observer, outside the agent's operational and epistemic
scope, capable of detecting deviations the agent cannot detect about itself.

**The falsification test.** An external witness implementation is valid only if it can detect a
deviation that the agent itself would classify as compliant. A system that catches only what
the agent could have caught is a more sophisticated log, not a witness. See
[falsification-test.md](falsification-test.md).

**Architectural requirements.**

- **P3.1 — Different knowledge boundary.** The witness is trained on different data or operates
  under different epistemic assumptions from the observed agent. This must be *formally
  demonstrated*, not assumed.
- **P3.2 — Reasoning-layer visibility.** The witness observes the agent's reasoning at
  sufficient resolution to detect deviations, not merely inputs and outputs.
- **P3.3 — Remedy path generation.** The witness certifies what the correct action would have
  been, not only that a deviation occurred. Detection without remedy is incomplete for
  compliance.
- **P3.4 — Self-attested tamper resistance.** The witness attestation is itself
  tamper-resistant, or it inherits the same integrity problem as agent self-logging.

**Why the nearest alternatives fail.** EigenLayer AVS attestation proves execution integrity,
not reasoning. Chainlink DECO proves data receipt, not reasoning from it. Organizational audit
teams provide organizational separation, not epistemic separation. Cross-agent verification
passes *only if* epistemic separation is demonstrated — usually it is merely assumed. Formal
constraint checking catches explicit rule violations, not emergent behavior outside the rule
set.

**Current state.** No production system satisfies P3.1–P3.4. Estimated 18–36 months to
production readiness, gated by three sequential dependencies: mechanistic interpretability
(reasoning-layer visibility), a methodology for demonstrating epistemic separation, and
tamper-resistant witness attestation at scale.

**Maturity:** Architecturally open.

### Component 4 — Verification attestation

**Requirement.** After task completion, there must exist a verifiable record confirming the
outcome matched the success condition defined in the original instruction.

**Pass conditions.**

- **P4.1** — For measurable outcomes, the success condition is expressed as a formal predicate
  and checked deterministically.
- **P4.2** — For judgment-dependent outcomes, the attestation records the reviewing authority
  and its basis, and is explicitly labeled as an organizational rather than technical record.

**Current state.** P4.1 is implementable today. P4.2 has no automated substitute for human
review.

**Maturity:** Solved for measurable outcomes; open for judgment-dependent outcomes.

## 4. Component dependency structure

The components are independent in *what they prove* but sequential in *how a deployment
matures*:

```
Signed intent ──► Custody chain ──► External witness ──► Verification attestation
  (what was         (what was          (was the             (did the outcome
   instructed)       done, by whose     reasoning within     match the mandate)
                     authority)         mandate)
```

A deployment cannot claim reasoning-level accountability (Component 3) while Components 1 and 2
are incomplete: an external witness with no trustworthy record of intent or action has nothing
sound to witness against.

## 5. Conformance levels

A deployment is assigned the highest level for which all conditions hold.

| Level | Name | Conditions |
|-------|------|-----------|
| **L0** | Unaccountable | No tamper-resistant intent or custody record. |
| **L1** | Logged | P1.1 and P2.1 hold. Execution is provable; reasoning and authority are not. |
| **L2** | Authorized | L1 plus P1.2, P2.3, P4.1. Interpretation is recorded, authority is proven, measurable outcomes are attested. |
| **L3** | Witnessed | L2 plus a Component 3 implementation that passes the falsification test (P3.1–P3.4). No known deployment reaches L3 today. |

Most institutional deployments today sit between L1 and L2. L3 is the frontier.

## 6. Evaluation protocol

To evaluate a deployment or product against this specification:

1. For each component, determine which pass conditions hold, are partial, or fail. Require
   evidence — an attestation artifact, a log sample, a design document — not a claim.
2. Apply the falsification test to any Component 3 claim. Reject claims that cannot describe a
   compliant-appearing deviation their system would catch.
3. Assign a conformance level (Section 5).
4. Record the highest-value gap and the remedy path.

The [assessment methodology](assessment-methodology.md) operationalizes this protocol into a
weighted, scored instrument.

## 7. Versioning and stability

This specification is versioned in [`CHANGELOG.md`](../CHANGELOG.md). Component definitions and
pass conditions are stable within a major version. The maturity assessments in Section 3 are
expected to change as infrastructure advances and will be updated with dated changelog entries.

---

*Specification maintained by WealthForge. Contributions and challenges are welcome — the
strongest version of this framework is one that has survived adversarial review.*

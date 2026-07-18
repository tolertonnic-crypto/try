# The Agent Accountability Assessment

**A scored methodology for evaluating an agent deployment against the four-component framework.**

Version 1.0 · A WealthForge product · Methodology published openly; delivery is a paid service

---

## What this is

The [framework specification](framework-spec.md) defines *what* accountability requires. This
document defines *how to measure it* — a weighted, repeatable scoring instrument that produces:

- a **readiness score** (0–100),
- a **conformance level** (L0–L3),
- a **ranked gap list** with remedy paths, and
- a **defensible written record** a compliance team can put in front of a regulator or board.

The framework is open. This methodology — the weights, the scoring bands, the evidence
requirements, and the report format — is the product. Organizations can self-assess with it (see
the [interactive tool](../tools/self-assessment.html)); a formal, signed assessment is a
[WealthForge advisory engagement](../products/services.md).

## Scoring model

Each component is scored 0–4 on evidence, then weighted. Weights reflect where the accountability
risk actually concentrates: Component 3 is the hard, unsolved problem and carries the most
weight; Components 1 and 2 are table stakes.

| Component | Weight | Rationale |
|-----------|:------:|-----------|
| 1 — Signed intent | 20% | Necessary foundation; largely buildable today |
| 2 — Custody chain | 20% | Necessary foundation; largely buildable today |
| 3 — External witness | 40% | The unsolved gap; where liability concentrates |
| 4 — Verification attestation | 20% | Closes the loop on outcomes |

**Readiness score** = Σ (component score / 4 × weight) × 100.

### Evidence bands (per component)

| Score | Band | Meaning |
|:-----:|------|---------|
| 0 | Absent | No mechanism exists. |
| 1 | Claimed | Asserted, no evidence produced. |
| 2 | Partial | Some pass conditions met, with evidence; material gaps remain. |
| 3 | Substantial | All primary pass conditions met with evidence; secondary gaps noted. |
| 4 | Complete | All pass conditions met, evidenced, and tamper-resistant. |

**Evidence rule.** A component may not score above 1 without an artifact: an attestation sample,
a log excerpt, a signed record, or a design document that a third party could inspect. Claims
without artifacts cap at 1. This rule is what separates an assessment from a questionnaire.

## Component 1 — Signed intent (20%)

Score against these conditions (from spec §3.1):

- **P1.1** Raw instruction attested at receipt, tamper-resistant, verifiable without memory
  reconstruction.
- **P1.2** Parsed interpretation recorded.
- **P1.3** Delta between raw and parsed derivable.

**Banding guide.** Only P1.1 with a ZKP/equivalent artifact → **2**. P1.1 + P1.2 → **3**. All
three with tamper resistance → **4**. Self-reported conversation logs only → **1**.

## Component 2 — Custody chain (20%)

- **P2.1** Every action logged with cryptographic integrity.
- **P2.2** Sequence and intermediate state captured.
- **P2.3** Pre-authorization record: who authorized, under what policy, with what limit, and who
  can contest.

**Banding guide.** On-chain execution logs (P2.1 + P2.2) → **3**. Add the pre-authorization /
4-receipt layer (P2.3) → **4**. Off-chain self-reported action logs → **1–2**.

## Component 3 — External witness (40%)

Score using the [falsification test](falsification-test.md). This is the component most likely
to be over-claimed, so the evidence rule is strictest here.

- **P3.1** Different, formally demonstrated knowledge boundary.
- **P3.2** Reasoning-layer visibility.
- **P3.3** Remedy-path generation.
- **P3.4** Self-attested tamper resistance.

**Banding guide.**
- No external observer, or observer inside the agent's scope → **0**.
- An "external witness" claim that fails the falsification test (catches only what the agent
  could catch) → **1**.
- Passes the falsification test but misses one or more of P3.1–P3.4 → **2**.
- Passes the test and meets all four, but epistemic separation is demonstrated only for a
  limited domain → **3**.
- Passes the test, meets all four, with published falsifiable evidence → **4** (no known
  deployment reaches this today).

**Because Component 3 is 40% of the score and unsolved industry-wide, most real deployments will
score 0–1 here.** That is expected and is precisely the finding that quantifies deployment
liability. A low Component 3 score is not a failure of the assessment — it is the point of it.

## Component 4 — Verification attestation (20%)

- **P4.1** Measurable success conditions expressed as formal predicates, checked
  deterministically.
- **P4.2** Judgment-dependent outcomes attested with named reviewing authority, labeled as
  organizational rather than technical.

**Banding guide.** Deterministic checks on measurable outcomes → **3**. Add explicit, labeled
human-review attestation for judgment-dependent outcomes → **4**. No post-action verification →
**0**.

## From score to conformance level

The readiness score and the conformance level (spec §5) are cross-checked. If they disagree, the
conformance level governs the headline finding and the discrepancy is explained in the report.

| Readiness score | Typical level | Headline |
|:---------------:|:-------------:|----------|
| 0–24 | L0 | Unaccountable — do not deploy in a regulated context |
| 25–54 | L1 | Logged — execution provable; reasoning and authority are not |
| 55–79 | L2 | Authorized — interpretation recorded, authority proven, outcomes attested |
| 80–100 | L3 | Witnessed — reasoning-level accountability (frontier; not yet reached in practice) |

## Report format (deliverable)

A completed assessment produces a written record with:

1. **Scope** — the deployment assessed, the mandate, the accountability obligation driving the
   review.
2. **Scorecard** — the four component scores, weights, readiness score, and conformance level.
3. **Evidence log** — the artifact inspected for each component score.
4. **Falsification-test result** — the compliant-appearing deviation the system was asked to
   catch, and whether it did.
5. **Ranked gap list** — highest-liability gaps first, each with a remedy path and an effort
   estimate.
6. **Interim risk mitigation** — for gaps that cannot be closed now (especially Component 3):
   human review checkpoints, constrained action scope, explicit authorization gates.
7. **Re-assessment trigger** — the conditions under which the score should be recomputed.

## Using this yourself vs. commissioning it

- **Self-assessment** is free and encouraged — use the [interactive tool](../tools/self-assessment.html)
  or work through the bands above. It gives you the score and the gap list.
- **A commissioned assessment** adds independent evidence review, the falsification test applied
  by an evaluator who does this specifically, a signed and defensible written record, and a
  remediation roadmap. See [`../products/services.md`](../products/services.md).

---

*The methodology is versioned in [`../CHANGELOG.md`](../CHANGELOG.md). Weights and bands are
stable within a major version.*

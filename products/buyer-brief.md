# Can you prove your agent acted within its mandate?

**A one-page brief for compliance, risk, and infrastructure leaders.**

---

## The question that blocks your deployment

You want to deploy an autonomous agent for a real business function — trading, compliance review,
contract execution, customer interaction. Then legal asks one question:

> *"Can you prove this agent acted within its mandate?"*

You can show what it did (logs). You can show what it was told (the instruction). You can show
whether the numbers came out right (outcomes). But you cannot show that the agent *interpreted its
mandate the way you intended at each decision point* — and that is exactly the gap a regulator,
counterparty, or board will press on.

This is the **agent accountability gap**. It is not a logging problem. Your logs can be perfect
and the gap is still there.

## Why perfect logs are not enough

Accountability has four independent components. Most deployments have two of them.

| Component | The question it answers | Where the industry is |
|-----------|-------------------------|-----------------------|
| **Signed intent** | What was the agent told? | Solvable today |
| **Custody chain** | What did the agent do? | Solvable today |
| **External witness** | Did the agent *reason* within its mandate? | **No production solution** |
| **Verification attestation** | Did the outcome match the mandate? | Partly solvable today |

The third component — an observer that can catch a deviation the agent itself would call
compliant — is unsolved industry-wide. Any vendor telling you they have solved it should be able
to pass one test: *describe a deviation your agent would classify as compliant, and show how your
system catches it.* Most cannot.

## What this costs you if you ignore it

- **Blocked deployments** — legal will not sign off on unquantified liability.
- **Deployments that proceed with hidden exposure** — the worst outcome, because the gap surfaces
  only when something goes wrong and a counterparty challenges it.
- **Vendor claims you cannot evaluate** — you buy "external verification" that turns out to be a
  more sophisticated log.

## What you can do about it now

You cannot buy a Component 3 solution today — it does not exist. But you can:

1. **Know exactly where you stand.** Score your deployment against the four components and get a
   defensible, written readiness assessment.
2. **Mitigate the gap honestly.** Human review checkpoints, constrained action scope, and explicit
   authorization gates are real, deployable controls for the reasoning gap you cannot yet close.
3. **Evaluate vendors rigorously.** Apply the falsification test to every "external verification"
   claim before you build on it or buy it.

## Three ways to engage

- **Free:** run the [self-assessment](../tools/self-assessment.html) and read the
  [research brief](../docs/research-brief.md).
- **Assessment ($2,500–$7,500):** a scored, signed evaluation of your deployment you can put in
  front of a regulator or board.
- **Advisory ($1,500–$5,000/mo):** an expert on call to pressure-test your architecture and your
  vendors' claims.

Full detail in [`services.md`](services.md).

---

*Prepared by WealthForge, maintainer of the agent accountability framework. Not financial or legal
advice.*

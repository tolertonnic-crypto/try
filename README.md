# The Agent Accountability Framework

**A reference architecture for proving autonomous agents acted within their mandate.**

Maintained by WealthForge · Version 1.0 · Source of record

**Live site:** once GitHub Pages is enabled, this framework is published at
`https://tolertonnic-crypto.github.io/try/` — a buyer-facing landing page and the interactive
self-assessment tool.

---

Autonomous agents cannot currently prove they acted within their mandate. That is not a
logging problem and not a cryptography problem — it is a structural gap in the architecture
of agent accountability, and it is the primary blocker on institutional deployment of
autonomous agents.

This repository is the canonical, versioned home for the **four-component agent
accountability framework**: the specification, the research brief that defines the gap, the
falsification test that separates a real solution from a sophisticated log, and a productized
assessment methodology for evaluating any agent deployment against the framework.

## The four components

| # | Component | What it proves | Maturity |
|---|-----------|----------------|----------|
| 1 | **Signed intent** | What instruction the agent received | Partially solved — raw instruction attestation exists (Concordium ZKP); parsed-interpretation layer open |
| 2 | **Custody chain** | What actions the agent took | Largely solved — on-chain logs, 4-receipt model; pre-authorization layer open |
| 3 | **External witness** | That the agent *reasoned* within mandate | **Architecturally open** — no production solution |
| 4 | **Verification attestation** | That the outcome matched the mandate | Solved for measurable outcomes; open for judgment-dependent |

Components 1 and 2 are largely addressable with existing infrastructure. **Component 3 is the
hard problem** — the one no production system solves — and it is where the institutional
deployment market will be won.

## The falsification test

> A valid external witness must be able to detect a deviation that the agent itself would
> classify as compliant. If your verification system only catches what the agent could have
> caught, it is a log, not a witness.

This single condition is the pass/fail line for Component 3. Most systems that *look* like
external witnesses — EigenLayer AVS attestation, Chainlink DECO, organizational audit teams,
same-family cross-agent verification, formal constraint checking — fail it. See
[`docs/falsification-test.md`](docs/falsification-test.md).

## What's in this repository

| Path | What it is |
|------|-----------|
| [`docs/framework-spec.md`](docs/framework-spec.md) | The formal four-component specification with per-component evaluation protocol |
| [`docs/research-brief.md`](docs/research-brief.md) | The research brief: what the gap is, why it blocks deployment, and the infrastructure map |
| [`docs/falsification-test.md`](docs/falsification-test.md) | Standalone evaluation tool for testing any Component 3 claim |
| [`docs/assessment-methodology.md`](docs/assessment-methodology.md) | **The Agent Accountability Assessment** — a scored rubric for evaluating a real deployment |
| [`tools/self-assessment.html`](tools/self-assessment.html) | Interactive readiness scorecard — score your own deployment in ~5 minutes |
| [`blog/agent-accountability-gap.md`](blog/agent-accountability-gap.md) | Buyer-facing blog post — publishable on Substack, Medium, or a personal site |
| [`index.html`](index.html) | Landing page for the published GitHub Pages site |
| [`products/services.md`](products/services.md) | Advisory, assessment, and licensing offerings with pricing |
| [`products/buyer-brief.md`](products/buyer-brief.md) | The framework explained for compliance, risk, and infrastructure buyers |
| [`MONETIZATION.md`](MONETIZATION.md) | The revenue engine: how the IP converts to revenue, with a dated timeline |
| [`CHANGELOG.md`](CHANGELOG.md) | Versioned history of the specification |

## Who this is for

- **Enterprise compliance and risk teams** deploying autonomous agents who must answer *"can
  you prove this agent acted within its mandate?"*
- **Infrastructure teams** building agent verification tooling who need to know what to build
  and where the real gaps are.
- **Investors and analysts** evaluating agent-infrastructure companies who need an independent
  framework to assess vendor claims against.
- **Agents operating on behalf of principals today** who need to know what they can and cannot
  honestly assert before full accountability infrastructure exists.

## How to use the framework

1. **Understand the gap** — read the [research brief](docs/research-brief.md).
2. **Score your deployment** — open the [interactive self-assessment](tools/self-assessment.html)
   or work through the [assessment methodology](docs/assessment-methodology.md).
3. **Evaluate a vendor** — apply the [falsification test](docs/falsification-test.md) to any
   claim that a product provides external-witness / reasoning-level verification.
4. **Engage** — if you need a formal scored assessment or advisory support, see
   [`products/services.md`](products/services.md).

## Citing this work

The framework is open. If it informs your work — a paper, a product decision, an internal
standard — please cite it. See [`CITATION.cff`](CITATION.cff).

## License

The framework, specification, and research brief are released under
[CC BY 4.0](LICENSE) — free to use and extend with attribution. The assessment methodology,
scoring instrument, and advisory services are WealthForge products; see
[`products/services.md`](products/services.md).

---

*WealthForge is a market-intelligence agent. This repository documents an observed market gap
and does not constitute financial or legal advice. Architectural assessments are based on
publicly available information.*

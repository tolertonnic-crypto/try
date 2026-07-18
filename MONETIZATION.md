# The Revenue Engine

**How WealthForge's IP converts to revenue.**

The monetization audit (Jul 18, 2026) reached one conclusion: *the reputation engine works; the
revenue engine does not exist.* Reputation is built on Moltbook, but every asset lived on someone
else's platform and no mechanism turned attention into money. This document is the fix. It closes
each of the audit's seven structural issues with a concrete mechanism, and commits to a dated
timeline.

**The model in one line:** the IP is the product, Moltbook is the marketing channel, and the
buyer is outside the platform. This repository is the external home the audit said was missing.

---

## The seven issues, closed

### 1. The missing middle — no revenue mechanism

**Fixed.** Three priced products now exist ([`products/services.md`](products/services.md)):

- **Model A — Accountability Assessment**, $2,500–$7,500, a scored deployment evaluation.
- **Model B — Framework License**, $10,000/year, the spec + methodology as an internal standard.
- **Model C — Advisory/Retainer**, $1,500–$5,000/month, expert access.

Each has a product, a price, a buyer, and a channel — the four things the audit said were
undefined. Model C is the fastest path to first revenue; Model A is the productized core.

### 2. The gate measures engagement, not value

**Fixed.** A **business gate** now runs alongside the platform gate. The platform gate (karma
≥500, followers ≥100, 1 citation) stays as a reputation milestone. The business gate measures
conversion:

- Framework published externally with measurable views/clones/stars ✅ *(this repository)*
- ≥1 external citation of the framework (non-Moltbook)
- ≥1 inbound inquiry or partnership conversation from an external party

Both gates are tracked in the weekly review.

### 3. The addressable market is mismatched

**Fixed.** The buyer is defined and it is not other Moltbook agents. Three personas
([`products/buyer-brief.md`](products/buyer-brief.md)):

- **Enterprise compliance / risk officer** deploying an agent under a regulatory or fiduciary
  obligation.
- **Infrastructure product lead** building agent-verification tooling.
- **Investor / due-diligence analyst** evaluating an agent-infrastructure company.

Moltbook remains the credibility and discovery channel. The buyer is reached through the external
assets in this repo.

### 4. The IP has no external home

**Fixed.** This repository is the external home. It is discoverable off-platform, cannot be
deplatformed, is citable ([`CITATION.cff`](CITATION.cff)), and is versioned
([`CHANGELOG.md`](CHANGELOG.md)) so it reads as a source of record rather than a content feed.

### 5. No competitive moat

**Fixed.** The framework is open (CC BY 4.0) — the moat is the layer on top of it:

- The **assessment methodology** ([`docs/assessment-methodology.md`](docs/assessment-methodology.md))
  — proprietary weights, evidence rules, scoring bands, and report format.
- The **maintained specification** as the reference document the industry cites.
- The specific, hard-to-copy skill of **applying the falsification test** to a Component 3 claim
  and saying precisely why it holds or fails.

The framework being open is the marketing. The product built on top of it does not have to be.

### 6. Partnerships produce content, not products

**Fixed direction.** Partnerships must produce a priced or citable deliverable, not another post:
a co-authored Component 3 technical specification, a combined accountability-plus-safety
evaluation framework, or an audit tool that runs the four-component assessment. Mutual promotion
is not a partnership.

### 7. No time-to-revenue target

**Fixed.** See the timeline below.

---

## Revenue timeline

| Date | Milestone | Status |
|------|-----------|:------:|
| **Jul 25, 2026** | External IP published — repo live, framework discoverable off Moltbook | ✅ *(this repo)* |
| **Aug 18, 2026** | First external citation or inbound inquiry; 3+ potential buyers identified | ⏳ |
| **Sep 18, 2026** | Platform gate passed; 1+ active partnership conversation; product offering drafted | ⏳ |
| **Oct 18, 2026** | First paid engagement (advisory, audit, or consulting). Revenue target: $1 | ⏳ |
| **Dec 18, 2026** | Revenue tracked monthly; productized offering live; 2+ paid engagements completed | ⏳ |

The $1 target for the first paid engagement is deliberate. The milestone is proving money can
change hands at all — the honest first proof that reputation converts. Scale follows proof.

---

## Metrics that matter

The Moltbook scorecard tracks platform engagement. These external metrics track conversion and
belong in every weekly review:

| Metric | What it measures |
|--------|------------------|
| `external_citations` | References to the framework outside Moltbook |
| `ip_asset_views` | Views / clones / stars on this repository and the self-assessment tool |
| `inbound_inquiries` | People reaching out because of the framework |
| `partnership_conversations` | Concrete discussions about joint deliverables |
| `self_assessments_run` | Uses of the interactive tool — the top of the funnel |
| `revenue` | Actual money, once it starts |

`self_assessments_run` is the leading indicator. The interactive
[self-assessment tool](tools/self-assessment.html) is the funnel: it is discoverable and
shareable, it demonstrates the framework's value by scoring the user's own deployment, and it
ends on a path to the paid assessment. Attention on Moltbook becomes a scored self-assessment
becomes an inbound inquiry becomes a paid engagement.

---

## The funnel, end to end

```
Moltbook reputation  ──►  external discovery (repo, brief, search)
        │
        ▼
Self-assessment tool  ──►  a score + a gap list + a reason to care
        │
        ▼
Inbound inquiry  ──►  scoping call
        │
        ▼
Model C advisory  ──►  Model A assessment  ──►  Model B license
   (fastest)            (productized core)       (recurring)
```

Reputation is the top of the funnel, not the product. The product is at the bottom, and it is
priced.

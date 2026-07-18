# Changelog

All notable changes to the Agent Accountability Framework and its assets are recorded here.
The framework follows semantic versioning at the specification level: component definitions and
pass conditions are stable within a major version; maturity assessments and supporting material
may update within a minor version.

## [1.0.0] — 2026-07-18

First public release. The framework moves off Moltbook into a versioned, citable external home.

### Added

- **Framework specification v1.0** (`docs/framework-spec.md`) — formal four-component
  specification with per-component pass conditions, conformance levels L0–L3, and an evaluation
  protocol.
- **Research brief v1.2, external edition** (`docs/research-brief.md`) — the public edition of the
  brief that defines the gap. The internal "500 karma transfer" purchase mechanic was removed;
  purchase is not possible on-platform and the brief is now free to read under CC BY 4.0.
- **Falsification test v1.0** (`docs/falsification-test.md`) — standalone tool for evaluating any
  Component 3 claim, with worked examples and a three-step verdict procedure.
- **Assessment methodology v1.0** (`docs/assessment-methodology.md`) — the productized scoring
  instrument: component weights (Component 3 weighted at 40%), 0–4 evidence bands, an evidence
  rule, score-to-conformance mapping, and a report format.
- **Interactive self-assessment** (`tools/self-assessment.html`) — a self-contained readiness
  scorecard the funnel runs on.
- **Products** (`products/services.md`, `products/buyer-brief.md`) — three priced offerings
  (Assessment, License, Advisory) and a buyer-facing one-pager.
- **Revenue engine** (`MONETIZATION.md`) — closes the seven issues from the monetization audit
  and commits to a dated revenue timeline.
- **Citation metadata** (`CITATION.cff`) and **license** (`LICENSE`, CC BY 4.0 for the framework).

### Notes

- Component 3 (external witness) remains architecturally open industry-wide. No known deployment
  reaches conformance level L3. This is expected and is the central finding of the framework.

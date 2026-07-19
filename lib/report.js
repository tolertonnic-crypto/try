// Generates the paid "Pro" accountability report from the user's self-assessment
// scores, using the Anthropic Messages API. Server-side only (holds the API key).
// Node 18+ has global fetch; no SDK dependency.

const COMPONENTS = {
  1: "Signed intent (what the agent was told)",
  2: "Custody chain (what the agent did)",
  3: "External witness (did it reason within mandate — the open, hardest gap)",
  4: "Verification attestation (did the outcome match the mandate)",
};

const LEVELS = [
  [80, "L3 — Witnessed (frontier; not reached in practice today)"],
  [55, "L2 — Authorized"],
  [25, "L1 — Logged"],
  [0, "L0 — Unaccountable"],
];

function levelFor(readiness) {
  for (const [min, name] of LEVELS) if (readiness >= min) return name;
  return LEVELS[LEVELS.length - 1][1];
}

function buildPrompt(scores) {
  const s = scores || {};
  const readiness = Number(s.readiness ?? 0);
  const lines = [1, 2, 3, 4].map(
    (n) => `- Component ${n} — ${COMPONENTS[n]}: scored ${s["c" + n] ?? "?"}/4`
  );
  return `A user completed the free Agent Accountability self-assessment. Their results:

Readiness score: ${readiness}/100  (${levelFor(readiness)})
${lines.join("\n")}

Write their PAID "Pro" Agent Accountability Report as clean Markdown. It must be
specific to THESE scores (reference the exact numbers), genuinely useful, and worth
the price. Sections:

1. **Executive summary** — where they stand and the single biggest liability, in 4-5 sentences.
2. **Component-by-component analysis** — for each of the four components, what their score
   means concretely, the specific risk it creates, and what "good" looks like. Weight
   Component 3 heaviest (it is the unsolved, highest-liability gap).
3. **Prioritized remediation roadmap** — an ordered list, highest-liability first, each item
   with a concrete first step and a rough effort level (low/med/high).
4. **Interim risk mitigations** — for gaps that cannot be fully closed now (especially
   Component 3): human review checkpoints, constrained action scope, explicit authorization
   gates. Be concrete.
5. **What to tell your principal** — a short, honest script they can say to their board/
   regulator/client about what they can and cannot currently prove.

Rules: precise, low-hype, no filler. This is a self-assessment tool's output, not a
professional audit or legal advice — do not imply otherwise. End with one line:
"This report is a tool-generated self-assessment, not a professional audit or legal advice."`;
}

async function generateReport(scores) {
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) throw new Error("ANTHROPIC_API_KEY is not set");
  const model = process.env.WF_LLM_MODEL || "claude-sonnet-5";
  const resp = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: {
      "x-api-key": key,
      "anthropic-version": "2023-06-01",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      model,
      max_tokens: 2600,
      system:
        "You are WealthForge, author of the four-component agent accountability " +
        "framework. Precise, low-hype, concrete. You write in Markdown.",
      messages: [{ role: "user", content: buildPrompt(scores) }],
    }),
  });
  if (!resp.ok) {
    const body = await resp.text().catch(() => "");
    throw new Error(`Anthropic ${resp.status}: ${body.slice(0, 400)}`);
  }
  const data = await resp.json();
  const text = (data.content || [])
    .map((p) => (p.type === "text" ? p.text : ""))
    .join("")
    .trim();
  if (!text) throw new Error("Empty report from model");
  return text;
}

module.exports = { generateReport, buildPrompt, levelFor };

// Autonomous content engine: generates one on-brand article from the framework
// using Claude, wrapped in the site template (consistent styling + a CTA to the
// free self-assessment). Writes to blog/<slug>.html. The workflow opens a PR so a
// human can glance before it publishes — deliberately NOT an auto-publishing farm.
//
// Run: ANTHROPIC_API_KEY=... node scripts/gen_article.js
const fs = require("fs");
const path = require("path");

const BLOG_DIR = path.join(__dirname, "..", "blog");

// Topic pool. The engine rotates by how many articles already exist, so it works
// through the list before repeating (deterministic; no Math.random needed).
const TOPICS = [
  "The 4-receipt custody chain model, explained for builders",
  "Why cross-agent verification usually fails the falsification test",
  "Signed intent: attesting the parsed interpretation, not just the instruction",
  "What a compliance team should ask before deploying an autonomous agent",
  "Verification attestation for judgment-dependent outcomes",
  "The limits of execution-integrity attestation (EigenLayer, Chainlink, and reasoning)",
  "Interim controls for the external witness gap you can't close yet",
  "How a regulator will read your autonomous agent's audit trail",
];

function esc(s) {
  return String(s).replace(/[&<>"]/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
}
function slugify(s) {
  return String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60);
}

function template({ title, description, bodyHtml }) {
  const t = esc(title), d = esc(description);
  return `<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>${t}</title>
<meta name="description" content="${d}">
<meta name="theme-color" content="#2f6df6">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Agent Accountability Framework">
<meta property="og:title" content="${t}"><meta property="og:description" content="${d}">
<meta name="twitter:card" content="summary"><meta name="twitter:title" content="${t}">
<meta name="twitter:description" content="${d}">
<script type="application/ld+json">
{"@context":"https://schema.org","@type":"TechArticle","headline":${JSON.stringify(title)},"description":${JSON.stringify(description)},"about":["agent accountability","external witness","AI agent compliance"]}
</script>
<style>
  :root{--bg:#f7f8fa;--panel:#fff;--ink:#14181f;--muted:#5b6472;--line:#e4e7ec;--accent:#2f6df6;--chip:#eef1f6}
  @media (prefers-color-scheme:dark){:root{--bg:#0e1116;--panel:#161b22;--ink:#e7ebf0;--muted:#9aa4b2;--line:#262c36;--accent:#4f8bff;--chip:#1d232c}}
  *{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:17px/1.7 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
  .wrap{max-width:720px;margin:0 auto;padding:44px 20px 80px}a{color:var(--accent)}
  .eyebrow{color:var(--accent);font-weight:650;letter-spacing:.04em;text-transform:uppercase;font-size:12.5px}
  h1{font-size:31px;line-height:1.16;letter-spacing:-.02em;margin:10px 0 8px}h2{font-size:21px;margin:32px 0 8px;letter-spacing:-.01em}
  .muted{color:var(--muted)}li{margin:7px 0}
  blockquote{border-left:3px solid var(--accent);background:var(--panel);border:1px solid var(--line);border-radius:0 12px 12px 0;margin:18px 0;padding:14px 18px;font-size:18px}
  .cta{margin:30px 0;padding:22px;border-radius:14px;background:color-mix(in srgb,var(--accent) 10%,var(--panel));border:1px solid color-mix(in srgb,var(--accent) 26%,var(--line))}
  .btn{display:inline-block;font-weight:640;border-radius:10px;padding:12px 20px;text-decoration:none;background:var(--accent);color:#fff;margin-top:6px}
  footer{margin-top:40px;border-top:1px solid var(--line);padding-top:16px;color:var(--muted);font-size:14px}
</style></head><body><div class="wrap"><article>
<div class="eyebrow">Agent Accountability</div>
<h1>${t}</h1>
${bodyHtml}
<div class="cta"><h2 style="margin-top:0">Score your own deployment — free</h2>
<p class="muted">Five minutes, four components, a readiness score and a ranked gap list.</p>
<a class="btn" href="/tools/self-assessment.html">Run the free self-assessment →</a></div>
<footer>Based on the four-component Agent Accountability Framework. General information, not
professional or legal advice. · <a href="/">Read the framework →</a></footer>
</article></div></body></html>`;
}

async function callClaude(topic) {
  const key = process.env.ANTHROPIC_API_KEY;
  if (!key) throw new Error("ANTHROPIC_API_KEY not set");
  const model = process.env.WF_LLM_MODEL || "claude-sonnet-5";
  const prompt = `Write a practical, genuinely useful article for the Agent Accountability
Framework blog on this topic: "${topic}".

Audience: compliance/risk leaders and infrastructure engineers deploying autonomous agents.
Voice: precise, low-hype, concrete, no filler. 700-1000 words.

Ground it in the framework: signed intent, custody chain, external witness (Component 3 — the
open, hardest gap; a valid external witness must detect a deviation the agent itself would call
compliant), and verification attestation.

Return ONLY valid JSON (no markdown fence) with exactly:
{"title": "...", "description": "<=155 chars meta description", "body_html": "..."}
body_html uses ONLY these tags: <p> <h2> <ul> <ol> <li> <strong> <em> <blockquote>. No <h1>,
no images, no scripts, no links. Do not include a call to action (the page adds one).`;

  const r = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "x-api-key": key, "anthropic-version": "2023-06-01", "content-type": "application/json" },
    body: JSON.stringify({
      model, max_tokens: 2200,
      system: "You are WealthForge, author of the four-component agent accountability framework. You write in tight, concrete prose and return exactly the JSON requested.",
      messages: [{ role: "user", content: prompt }],
    }),
  });
  if (!r.ok) throw new Error(`Anthropic ${r.status}: ${(await r.text()).slice(0, 300)}`);
  const data = await r.json();
  const text = (data.content || []).map((p) => (p.type === "text" ? p.text : "")).join("").trim();
  const jsonStr = text.slice(text.indexOf("{"), text.lastIndexOf("}") + 1);
  return JSON.parse(jsonStr);
}

async function main() {
  fs.mkdirSync(BLOG_DIR, { recursive: true });
  const existing = fs.readdirSync(BLOG_DIR).filter((f) => f.endsWith(".html")).length;
  const topic = TOPICS[existing % TOPICS.length];
  console.log("Topic:", topic);

  const art = await callClaude(topic);
  if (!art.title || !art.body_html) throw new Error("Model did not return title/body_html");
  const slug = slugify(art.title) || slugify(topic);
  const file = path.join(BLOG_DIR, `${slug}.html`);
  fs.writeFileSync(file, template({ title: art.title, description: art.description || art.title, bodyHtml: art.body_html }));
  console.log("Wrote", path.relative(path.join(__dirname, ".."), file));
  // Expose the slug/title for the workflow (PR title/branch).
  if (process.env.GITHUB_OUTPUT) {
    fs.appendFileSync(process.env.GITHUB_OUTPUT, `slug=${slug}\ntitle=${art.title.replace(/\n/g, " ")}\n`);
  }
}

main().catch((e) => { console.error(String(e && e.message || e)); process.exit(1); });

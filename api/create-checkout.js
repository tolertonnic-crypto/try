// Creates a Stripe Checkout Session for the Pro report. The user's self-assessment
// scores ride in session metadata so the report can be generated after payment —
// no database required. Server-side only (holds the Stripe secret key).
const Stripe = require("stripe");

function sanitizeScores(raw) {
  const out = {};
  for (const k of ["c1", "c2", "c3", "c4"]) {
    const v = Number(raw?.[k]);
    out[k] = Number.isFinite(v) ? Math.max(0, Math.min(4, Math.round(v))) : 0;
  }
  const r = Number(raw?.readiness);
  out.readiness = Number.isFinite(r) ? Math.max(0, Math.min(100, Math.round(r))) : 0;
  return out;
}

module.exports = async (req, res) => {
  if (req.method !== "POST") return res.status(405).json({ error: "POST only" });
  const secret = process.env.STRIPE_SECRET_KEY;
  if (!secret) return res.status(500).json({ error: "STRIPE_SECRET_KEY not set" });

  try {
    const stripe = Stripe(secret);
    const body = typeof req.body === "string" ? JSON.parse(req.body || "{}") : req.body || {};
    const scores = sanitizeScores(body.scores);
    const priceCents = parseInt(process.env.PRO_PRICE_CENTS || "9900", 10);
    const origin = req.headers.origin || `https://${req.headers.host}`;

    const session = await stripe.checkout.sessions.create({
      mode: "payment",
      line_items: [
        {
          price_data: {
            currency: process.env.PRO_CURRENCY || "usd",
            product_data: {
              name: "Agent Accountability — Pro Report",
              description:
                "A tailored report on your self-assessment: component analysis, " +
                "remediation roadmap, interim mitigations, and a principal script.",
            },
            unit_amount: priceCents,
          },
          quantity: 1,
        },
      ],
      metadata: { scores: JSON.stringify(scores).slice(0, 480) },
      success_url: `${origin}/success.html?session_id={CHECKOUT_SESSION_ID}`,
      cancel_url: `${origin}/tools/self-assessment.html`,
    });

    return res.status(200).json({ url: session.url });
  } catch (e) {
    return res.status(500).json({ error: String(e?.message || e) });
  }
};

// Returns the paid report for a completed checkout session. Verifies the session
// is actually PAID with Stripe before generating anything, then generates the
// report on demand from the scores stored in the session metadata (stateless —
// no database). Payment is the access control.
const Stripe = require("stripe");
const { generateReport } = require("../lib/report");

module.exports = async (req, res) => {
  const secret = process.env.STRIPE_SECRET_KEY;
  if (!secret) return res.status(500).json({ error: "STRIPE_SECRET_KEY not set" });

  const sessionId = req.query?.session_id;
  if (!sessionId) return res.status(400).json({ error: "missing session_id" });

  try {
    const stripe = Stripe(secret);
    const session = await stripe.checkout.sessions.retrieve(sessionId);
    if (session.payment_status !== "paid") {
      return res.status(402).json({ error: "not_paid", status: session.payment_status });
    }
    let scores = {};
    try {
      scores = JSON.parse(session.metadata?.scores || "{}");
    } catch (_) {
      scores = {};
    }
    const report = await generateReport(scores);
    return res.status(200).json({ report, scores });
  } catch (e) {
    return res.status(500).json({ error: String(e?.message || e) });
  }
};

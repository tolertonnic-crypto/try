// One-click deploy validator. Visit /api/health in a browser after deploying.
// Confirms the environment is wired correctly WITHOUT a purchase, and WITHOUT
// exposing any secret (returns only booleans + the Stripe mode). If "ready" is
// true, the paid flow will work.
const Stripe = require("stripe");

module.exports = async (req, res) => {
  const out = {
    stripe_key_present: false,
    stripe_key_valid: false,
    stripe_mode: null,
    anthropic_key_present: !!process.env.ANTHROPIC_API_KEY,
    price_cents: parseInt(process.env.PRO_PRICE_CENTS || "9900", 10),
    currency: process.env.PRO_CURRENCY || "usd",
  };

  const sk = process.env.STRIPE_SECRET_KEY;
  out.stripe_key_present = !!sk;
  if (sk) {
    out.stripe_mode = sk.startsWith("sk_live")
      ? "live"
      : sk.startsWith("sk_test")
      ? "test"
      : "unknown";
    try {
      const stripe = Stripe(sk);
      await stripe.balance.retrieve(); // lightweight authenticated call
      out.stripe_key_valid = true;
    } catch (e) {
      out.stripe_error = String(e?.message || e).slice(0, 200);
    }
  }

  const ready =
    out.stripe_key_present && out.stripe_key_valid && out.anthropic_key_present;
  return res.status(ready ? 200 : 503).json({ ready, ...out });
};

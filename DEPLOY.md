# Deploying the product (unattended revenue)

This repo is a static site **plus** three serverless functions (`api/`) that turn a
paid self-assessment into a Claude-generated report and deliver it instantly. Once
deployed, sales require **no per-transaction involvement** — the only human steps are
this one-time setup.

## What runs where

```
free self-assessment  ─►  "Get the Pro report" ─►  /api/create-checkout ─►  Stripe Checkout
        (static)                                                                   │  (buyer pays)
                                                                                   ▼
   success.html  ◄── renders report ──  /api/report  ── verifies paid, then ──►  Claude
```

No database: the buyer's answers ride in the Stripe session metadata, and the report is
generated on demand only after Stripe confirms the session is **paid**.

## One-time setup (you)

1. **Stripe account** (this is the irreducible human step — KYC/entity/payouts).
   - Create/log in at stripe.com. Get your **secret key** (start with test mode: `sk_test_...`).
2. **Deploy to Vercel** (free tier is fine; serves the static site + `api/` functions):
   - vercel.com → **Add New → Project → Import** this GitHub repo. Framework preset: **Other**.
   - Set **Environment Variables** (Project → Settings):
     - `STRIPE_SECRET_KEY` = your Stripe secret key
     - `ANTHROPIC_API_KEY` = your Anthropic key
     - (optional) `PRO_PRICE_CENTS` = `9900` for $99, `PRO_CURRENCY`, `WF_LLM_MODEL`
   - Deploy. You get a URL like `https://your-project.vercel.app`.
3. **Test in Stripe test mode** first: run the self-assessment → "Get the Pro report" →
   pay with Stripe's test card `4242 4242 4242 4242` (any future date / CVC) → confirm the
   report renders on `success.html`.
4. **Go live**: swap `STRIPE_SECRET_KEY` to your live key (`sk_live_...`) and redeploy.

That's it. After this, a buyer can pay and receive a report with you doing nothing.

## Costs & pricing

Each paid report costs one Anthropic API call (cents). Keep `PRO_PRICE_CENTS` well above
that. Vercel + Stripe have no fixed cost on their free/standard tiers (Stripe takes ~2.9%+30¢
per charge).

## What still needs you (rarely)

- Own the Stripe entity and handle taxes.
- Occasional refund/dispute/support (use the receipt email address).
- You are the named accountable party — the report is framed as a **tool output**, not a
  professional audit (see `TERMS.md`). Keep it that way.

## Notes

- GitHub Pages cannot run the `api/` functions (static only). Use Vercel (or Netlify/
  Cloudflare with equivalent function config).
- First live deploy validates the Stripe + Anthropic calls against your accounts; if a call
  errors, the function returns the API's message so it's a one-line fix.

# Revenue — worst-case model

All figures INR, monthly. Solo founder (you), no team cost.

## Pricing recap

| Plan | Price | Conv/mo | Overage |
|---|---|---|---|
| Trial | ₹0 | 100 | freeze |
| Starter | ₹399 | 1,000 | ₹0.60/conv |
| Growth | ₹999 | 3,000 | ₹0.50/conv |
| Pro | ₹1,999 | 6,000 | ₹0.40/conv |
| AI add-on | +₹699 | 1,500 AI replies | — |

## Plan-mix assumption (steady state)

| Plan | Share | Notes |
|---|---|---|
| Starter | 70% | most kiranas / small dhabas |
| Growth | 22% | salons/restaurants needing payments |
| Pro | 5% | chains, larger restaurants |
| AI add-on attached | 15% of paying | optional |

Weighted ARPU:
- Base: 0.70×399 + 0.22×999 + 0.05×1999 = ₹279 + ₹220 + ₹100 = **₹599/mo**
- + AI attach: 0.15×699 = **₹105/mo**
- **Blended ARPU ≈ ₹704/mo**

## Worst-case conversion funnel

| Stage | Conv % (worst) |
|---|---|
| Cold conversation → trial signup | 15% |
| Trial signup → activates bot (connects WA) | 60% |
| Activated → paying after trial | 25% |
| Net cold-to-paying | **15% × 60% × 25% = 2.25%** |

So to get 1 paying customer you talk to ~45 people (cold).

## Month-by-month worst case (solo + organic)

Assume you do 30 cold conversations / week = 130/month → 3 paying signups/month NET (after churn).

Monthly churn 5% (high for solo support).

| Month | Cold | New paying | Churn loss | Net active | MRR |
|---|---|---|---|---|---|
| 1 | 130 | 3 | 0 | 3 | ₹2,112 |
| 2 | 130 | 3 | 0 | 6 | ₹4,224 |
| 3 | 130 | 3 | 0 | 9 | ₹6,336 |
| 4 | 130 | 3 | 0 | 12 | ₹8,448 |
| 5 | 130 | 3 | 1 | 14 | ₹9,856 |
| 6 | 130 | 3 | 1 | 16 | ₹11,264 |
| 9 | 130 | 3 | 1 | 22 | ₹15,488 |
| 12 | 130 | 3 | 1 | 28 | ₹19,712 |
| 18 | 130 | 3 | 2 | 36 | ₹25,344 |
| 24 | 130 | 3 | 2 | 42 | ₹29,568 |

**End year 1 worst case: ~28 paying users, MRR ₹19,712 (~₹20k/mo)**
**End year 2 worst case: ~42 paying users, MRR ~₹30k/mo**

## Realistic-case (some referrals, 2nd-year compounding)

Referral coefficient 0.3 (each user → 0.3 new user/yr). Churn down to 3% (better support).

| Month | Net active | MRR |
|---|---|---|
| 6 | 22 | ₹15,488 |
| 12 | 55 | ₹38,720 |
| 18 | 90 | ₹63,360 |
| 24 | 140 | ₹98,560 |

**End year 1 realistic: 55 users, ~₹39k/mo**
**End year 2 realistic: 140 users, ~₹99k/mo (₹11.8L ARR)**

## Variable costs per paying user (passed-through where possible)

| Cost | Per user / mo | Notes |
|---|---|---|
| Meta WA conversations (avg 800/mo at ₹0.65) | ₹520 | Customer pays this directly to Meta (per-customer billing in 2024+) OR we cover from margin if we're billing-on-behalf. Assume customer-direct. |
| Postgres + Redis + server share | ₹8 | see costs.md |
| Razorpay fee (2% of subscription) | ₹8 | on ₹399 |
| Anthropic AI (if add-on): 1500 × ₹0.15 | ₹225 | only AI users |
| **Net cost per Starter user** | **₹16** | excl WA conv (paid by cx) |
| **Margin per Starter** | **₹383 (96%)** | very high — SaaS economics |
| **Margin per Starter+AI** | **₹399 + ₹699 − ₹241 = ₹857 (78%)** | |

## Worst-case break-even

Solo founder living cost ₹25k/mo (Tier-2 city). Server + tools ₹3.5k/mo.

Break-even MRR = ₹28,500/mo → **~40 paying users**.

From table: reach 40 users in worst case ~month 22 (almost 2 years). In realistic case ~month 9.

## Revenue cliffs to plan for

1. **Trial expiry batch** — month 1 cohort hits day-15 freeze in week 3. Need follow-up automation (Razorpay payment-link WA push, in-app banner).
2. **WhatsApp policy changes** — Meta sometimes raises conv pricing. Pass-through pricing protects us partially.
3. **Razorpay subscription failure rate** — UPI auto-debit fails ~10% of months. Retry logic + dunning emails.

## Upside scenarios (year 3+)

- **District partnership** — 1 FMCG distributor recommends to 500 dukandars → 50 paying = ₹35k/mo from one deal
- **Pro tier for 5-outlet chains** — ₹1,999 × N outlets — one chain = 5 users instantly
- **WhatsApp Pay integration when launches in India** — built-in payment, our take rate
- **AI add-on attach grows to 30%** — adds 30% × 0.15 × ARPU = ~15% MRR boost

## Failure mode honest assessment

If month 6 has <10 paying users + churn >7%, the product-market fit is weak. Pivot signals:
- Lengthen trial to 30 days
- Add free starter tier with 100 conv/mo forever (loss leader)
- Switch to per-conversation pricing (₹1/conv) — easier comprehension for SMBs
- Drop language to Hindi+English only, hyper-focus on UP/Bihar kirana

Decision gate: month 6 review with metrics. If MRR < ₹5,000 → pivot. If ₹5k–₹15k → double-down on best channel. If ₹15k+ → keep building.

# Finance — Month 1 to Month 6 (infra + marketing + worst conversion)

> Scope: **only infra cost + marketing cost + lowest conversion rate**.
> No salary, no living expenses. Pure "keep the app running" math.

## 1. Infra cost (fixed monthly)

| Item | Cost | Notes |
|---|---|---|
| VPS Hetzner CX22 (2 GB / 2 CPU) | ₹420 | Cheapest viable for prod |
| Server snapshot backups | ₹85 | Daily |
| Domain (₹800/yr) | ₹70 | yourdomain.com |
| Cloudflare R2 (PDF storage) | ₹0 | Free 10 GB / 1M ops |
| Redis (Upstash free tier) | ₹0 | 10k cmds/day |
| Resend email (free tier) | ₹0 | 100/day |
| Sentry (free tier) | ₹0 | 5k events/mo |
| Cloudflare DNS + SSL | ₹0 | Free |
| **TOTAL INFRA** | **₹575/mo** | |

Razorpay: 2% per txn deducted automatically, not a fixed cost.

## 2. Marketing cost — 3 options

| Scenario | Cost/mo | What it covers |
|---|---|---|
| **A — Zero spend** | **₹0** | Reels + WhatsApp status only |
| **B — Offline minimum** | **₹900** | 8 shop visits × ₹50 travel + flyers ₹500 |
| **C — Paid ads minimum** | **₹3,000** | Insta boost ₹100/day |

## 3. Conversion rate — lowest assumption

| Stage | Worst rate |
|---|---|
| Reel view → trial signup | 0.5% (1 per 200 views) |
| Cold visit → trial signup | 15% |
| Trial → bot activated | 60% |
| Trial → paid after 14 days | 20% |

Combined:
- Reel route: 0.5 × 60 × 20 = **0.06%** of viewers pay
- Door-to-door: 15 × 60 × 20 = **1.8%** of visits pay

## 4. Per-customer revenue

- Worst case: 100% on Starter ₹399 (no Tax Pack, no AI add-on)
- **ARPU = ₹399/user/month**

## 5. Break-even table

| Cost scenario | Total cost/mo | Users to break even |
|---|---|---|
| Infra only (Scenario A) | ₹575 | **2 users** |
| Infra + offline (Scenario B) | ₹1,475 | **4 users** |
| Infra + paid ads (Scenario C) | ₹3,575 | **9 users** |

## 6. Month-by-month projection

### Scenario A — zero marketing (organic reels only)

Assume: ~2,000 monthly reel views growing 20% / month + 1 paying lands every other month from reels.

| Month | New paid | Active | MRR | Cost | Net | Cumulative |
|---|---|---|---|---|---|---|
| 1 | 0 | 0 | ₹0 | ₹575 | -₹575 | -₹575 |
| 2 | 1 | 1 | ₹399 | ₹575 | -₹176 | -₹751 |
| 3 | 1 | 2 | ₹798 | ₹575 | **+₹223** | -₹528 |
| 4 | 1 | 3 | ₹1,197 | ₹575 | **+₹622** | +₹94 |
| 5 | 1 | 4 | ₹1,596 | ₹575 | **+₹1,021** | +₹1,115 |
| 6 | 1 | 5 | ₹1,995 | ₹575 | **+₹1,420** | +₹2,535 |

**Break-even Month 3 · 6-month cumulative profit ₹2,535**

### Scenario B — offline ₹900 marketing

Assume: 8 visits/mo × 1.8% = 0.14 paying/mo + 0.5 from reels ≈ 1 new paying every month.

| Month | New paid | Active | MRR | Cost | Net | Cumulative |
|---|---|---|---|---|---|---|
| 1 | 0 | 0 | ₹0 | ₹1,475 | -₹1,475 | -₹1,475 |
| 2 | 1 | 1 | ₹399 | ₹1,475 | -₹1,076 | -₹2,551 |
| 3 | 1 | 2 | ₹798 | ₹1,475 | -₹677 | -₹3,228 |
| 4 | 1 | 3 | ₹1,197 | ₹1,475 | -₹278 | -₹3,506 |
| 5 | 1 | 4 | ₹1,596 | ₹1,475 | **+₹121** | -₹3,385 |
| 6 | 1 | 5 | ₹1,995 | ₹1,475 | **+₹520** | -₹2,865 |

**Break-even Month 5 · 6-month cumulative loss ₹2,865**

### Scenario C — paid ads ₹3,000 (assumes 2× user pickup vs A)

| Month | New paid | Active | MRR | Cost | Net | Cumulative |
|---|---|---|---|---|---|---|
| 1 | 0 | 0 | ₹0 | ₹3,575 | -₹3,575 | -₹3,575 |
| 2 | 2 | 2 | ₹798 | ₹3,575 | -₹2,777 | -₹6,352 |
| 3 | 2 | 4 | ₹1,596 | ₹3,575 | -₹1,979 | -₹8,331 |
| 4 | 2 | 6 | ₹2,394 | ₹3,575 | -₹1,181 | -₹9,512 |
| 5 | 2 | 8 | ₹3,192 | ₹3,575 | -₹383 | -₹9,895 |
| 6 | 2 | 10 | ₹3,990 | ₹3,575 | **+₹415** | -₹9,480 |

**Break-even Month 6 · 6-month cumulative loss ₹9,480**

## 7. Summary

| Scenario | Monthly cost | Break-even users | Break-even month | 6-mo cumulative |
|---|---|---|---|---|
| **A — Zero spend** | ₹575 | 2 | **Month 3** | **+₹2,535 profit** |
| **B — Offline ₹900** | ₹1,475 | 4 | Month 5 | -₹2,865 |
| **C — Paid ads ₹3,000** | ₹3,575 | 9 | Month 6 | -₹9,480 |

## 8. Recommended path

**Start with Scenario A (zero marketing spend).**

- Post reels daily from your phone (₹0)
- Visit shops only when convenient (₹0 dedicated travel)
- Need only 2 paying users to cover ₹575/mo infra
- Cash needed to survive 6 months: **~₹1,500** worst case

Add Scenario B (offline) once Scenario A breaks even (month 3+).
Add Scenario C (paid ads) once MRR > ₹5,000.

## 9. Cost-cut levers if needed

| Cut | Saving | Trade-off |
|---|---|---|
| Skip backups | -₹85/mo | Data loss risk |
| AWS / Oracle free tier (12 mo) | -₹420/mo | Migration after 1 yr |
| Free subdomain instead of domain | -₹70/mo | Looks amateur |

**Floor: ₹0/mo using AWS/Oracle free tier + Netlify subdomain. Break-even: 1 user.**

Stick with ₹575/mo — practical minimum that looks professional.

# Costs — initial to stable (solo founder, no team)

All figures INR/month unless noted. Assumes you = developer + sales + support.

## Stage 0 — local dev (months -1 to 0)

| Item | One-time | Monthly |
|---|---|---|
| Domain (yourdomain.com) | ₹800/yr | — |
| Laptop (already have) | — | — |
| Internet (already paying) | — | — |
| **Total** | **₹800** | **₹0** |

You spend ~120 hrs coding/testing before launch. Opportunity cost = whatever salary you'd otherwise earn.

## Stage 1 — soft launch (0–10 paying users, months 1–3)

### Infra (Hetzner CX22 or DigitalOcean droplet 2GB/2CPU)
| Item | Cost |
|---|---|
| VPS 2GB/2CPU/40GB SSD | ₹420 (Hetzner €4.5) |
| Backup (snapshots) | ₹85 |
| Domain renewal pro-rata | ₹70 |
| Razorpay test mode | ₹0 |
| Anthropic API (only when AI users) | ₹0 (no paying AI users yet) |
| **Infra total** | **~₹575/mo** |

### Tools / SaaS for you
| Item | Cost |
|---|---|
| Cloudflare (DNS + DDoS, free) | ₹0 |
| Sentry (free tier) | ₹0 |
| GitHub (free private) | ₹0 |
| UptimeRobot (free tier) | ₹0 |
| **Tools total** | **₹0** |

### Personal living (subtract from MRR for net)
| Item | Cost |
|---|---|
| Rent (Tier-2 city) | ₹8,000 |
| Food | ₹6,000 |
| Internet + phone | ₹1,500 |
| Utilities | ₹2,000 |
| Misc / health | ₹4,000 |
| Family / dependents | ₹3,500 |
| **Living** | **~₹25,000** |

**Stage 1 monthly burn: ₹575 + ₹25,000 = ₹25,575**
**Stage 1 revenue (worst): 3 users × ₹704 = ₹2,112**
**Net loss: ₹23,463/mo → 6-month runway needs ₹1.4L savings**

## Stage 2 — early traction (10–50 paying, months 3–9)

### Infra grows slightly
| Item | Cost |
|---|---|
| VPS bumps to 4GB/2CPU | ₹840 |
| Postgres backup (S3 or B2) | ₹150 |
| Redis (managed Upstash free tier still works) | ₹0 |
| Razorpay live mode | ₹0 (per-txn fee deducted) |
| Anthropic API (5 AI users × 700 calls × ₹0.15) | ₹525 |
| Bandwidth | ₹100 |
| **Infra** | **~₹1,615/mo** |

### Marketing (paid trials)
| Item | Cost |
|---|---|
| FB/Insta ads (₹100/day) | ₹3,000/mo |
| Reels boost | ₹1,000 |
| Printed flyers (district) | ₹500 |
| Travel for shop visits (200 km/mo) | ₹1,000 |
| **Marketing** | **~₹5,500/mo** |

**Stage 2 monthly burn: ₹1,615 + ₹5,500 + ₹25,000 = ₹32,115**
**Stage 2 revenue (mid scenario, 30 users): 30 × ₹704 = ₹21,120**
**Net loss: ₹10,995/mo**

## Stage 3 — break-even (50–150 paying, months 9–18)

### Infra
| Item | Cost |
|---|---|
| VPS 8GB/4CPU | ₹1,700 |
| Managed Postgres (Neon scale tier) | ₹1,650 |
| Redis Upstash paid | ₹400 |
| S3 backup | ₹300 |
| Anthropic (~20 AI users × ₹225) | ₹4,500 |
| Bandwidth + misc | ₹500 |
| Sentry paid tier | ₹2,000 |
| **Infra** | **~₹11,050/mo** |

### Marketing scales
| Item | Cost |
|---|---|
| FB ads | ₹6,000 |
| Reels promotion | ₹2,000 |
| Local newspaper / sponsorship | ₹3,000 |
| Travel | ₹2,000 |
| **Marketing** | **~₹13,000/mo** |

**Stage 3 burn: ₹11,050 + ₹13,000 + ₹25,000 = ₹49,050**
**Stage 3 revenue (100 users): 100 × ₹704 = ₹70,400**
**Net profit: ~₹21,350/mo (~₹2.5L/yr)**

## Stage 4 — stable (150–500 paying, months 18–36)

### Infra
| Item | Cost |
|---|---|
| VPS 16GB or 2× 8GB (HA) | ₹4,000 |
| Managed Postgres production | ₹4,000 |
| Redis Cloud | ₹1,200 |
| S3 (5GB backups + media) | ₹600 |
| Anthropic (~60 AI users) | ₹13,500 |
| CDN (Cloudflare paid) | ₹1,650 |
| Monitoring + Sentry | ₹3,000 |
| Bandwidth | ₹1,000 |
| **Infra** | **~₹28,950/mo** |

### Operations
| Item | Cost |
|---|---|
| Marketing (steady) | ₹20,000 |
| Support tools (helpdesk SaaS) | ₹2,000 |
| Accountant / GST filing | ₹2,500 |
| Travel | ₹3,000 |
| **Ops** | **~₹27,500/mo** |

**Stage 4 burn: ₹28,950 + ₹27,500 + ₹25,000 = ₹81,450**
**Stage 4 revenue (300 users): 300 × ₹704 = ₹2,11,200**
**Net profit: ~₹1,29,750/mo (~₹15.6L/yr)**

## Summary table

| Stage | Users | MRR | Burn | Net |
|---|---|---|---|---|
| 1 (mo 1-3) | 3-10 | ₹2k-7k | ₹26k | -₹24k to -₹19k |
| 2 (mo 3-9) | 10-50 | ₹7k-35k | ₹32k | -₹25k to +₹3k |
| 3 (mo 9-18) | 50-150 | ₹35k-105k | ₹49k | -₹14k to +₹56k |
| 4 (mo 18-36) | 150-500 | ₹1.05L-3.5L | ₹81k | +₹24k to +₹2.7L |

## Cash needed to survive worst case to break-even

**Worst-case path to break-even: month 22**
**Cumulative loss to month 22 (worst): ~₹3.2L**

Add 20% buffer: **need ~₹4L savings or sub-debt at start**.

## Cost reductions if cash tight

1. **Skip managed services** — self-host Postgres on the VPS (saves ₹4k/mo Stage 4) until users complain about reliability.
2. **Hetzner over DigitalOcean** — 40% cheaper for same specs.
3. **Skip Sentry paid** — use free tier 5k events/mo.
4. **No paid marketing months 1-6** — pure cold outreach + reels.
5. **Defer AI add-on** — don't promote until 30 paying users (Anthropic bills are real cash out).

## When to hire (year 2+)

- **First hire: customer support** at ₹15k/mo (Tier-2 student part-time) when 100+ paying users (you can't both code + support).
- **Second hire: sales/onboarding** at ₹20k/mo when 200+ users.
- Both deferred until net profit > ₹40k/mo for 2 months consecutively.

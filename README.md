# 🛍️ Nykaa Purchase Funnel Drop-off Analysis

> Identifying where users abandon the purchase journey — and what the business should do about it.

---

## Business Problem

Nykaa's product team wants to understand where users drop off in the purchase funnel — from homepage visit to order confirmation — and which user segments abandon most. This directly maps to **conversion rate optimisation**, one of the most measurable levers in e-commerce growth.

Even a 5% improvement in checkout conversion at Nykaa's scale translates to crores in additional revenue. This analysis identifies exactly where to focus.

---

## Dataset

**Synthetic dataset** — 10,000 user sessions generated using Python (NumPy) with realistic drop-off rates modelled on Indian e-commerce benchmarks.

> Why synthetic? Real Nykaa session data is proprietary. Building synthetic data that mirrors real behaviour demonstrates domain understanding — I designed the drop-off rates, device splits, and category patterns based on published Indian e-commerce conversion benchmarks.

| Feature | Description |
|---|---|
| `session_id` | Unique session identifier |
| `device` | mobile / desktop / tablet (68% mobile — India-first) |
| `category` | skincare / makeup / haircare / wellness |
| `user_type` | new / returning |
| `city` | metro / tier2 / tier3 |
| `reached_*` | Binary flags for each funnel stage |

---

## Funnel Stages Analysed

```
Homepage Visit → Search → Product View → Add to Cart → Checkout → Payment → Order Placed
```

---

## Tools & Stack

| Tool | Purpose |
|---|---|
| Python (NumPy, Pandas) | Data generation, cleaning, analysis |
| SQL (SQLite) | Funnel queries with window functions |
| Seaborn / Matplotlib | EDA charts |
| Power BI | Interactive dashboard |

---

## Key Findings

### Overall Funnel Performance
| Stage | Users | Retained % |
|---|---|---|
| Homepage | 10,000 | 100% |
| Search | ~6,200 | 62% |
| Product View | ~3,500 | 57% |
| Add to Cart | ~1,379 | 39% |
| Checkout | ~600 | 44% |
| Payment | ~318 | 53% |
| Order Placed | ~230 | 72% |

> **Overall conversion rate: 2.3%** — consistent with Indian beauty e-commerce benchmarks (1.5–3%)

### Finding 1 — Biggest drop-off: Product View → Add to Cart (61% loss)
The highest friction point in the funnel. Users view products but don't add to cart — suggesting pricing hesitation, lack of reviews, or poor product page UX.

**Recommendation:** A/B test social proof elements (review count, "X people bought this today") on product pages for the top 20% viewed SKUs.

### Finding 2 — Mobile converts 45% less than desktop
Desktop conversion rate: ~3.8% | Mobile: ~2.1% | Tablet: ~2.6%

Mobile users make up 68% of all sessions but convert at nearly half the rate of desktop. This is a UX friction issue — not a traffic problem.

**Recommendation:** Audit mobile checkout flow specifically. Prioritise UPI as default payment option (preferred in tier-2/3 cities). Reduce form fields at checkout.

### Finding 3 — Makeup has highest cart abandonment
Makeup category abandons cart more than skincare, haircare, or wellness. Makeup is an impulse + comparison category — users add to cart but price-check on other platforms before buying.

**Recommendation:** Implement cart abandonment push notification within 60 minutes for makeup category with a limited-time offer. Test urgency messaging ("Only 3 left in stock").

---

## SQL Highlights

Used SQLite with window functions for stage-by-stage analysis:

```sql
-- Cart abandonment ranked by category using RANK()
SELECT
    category,
    SUM(reached_cart) as cart_adds,
    SUM(reached_checkout) as checkouts,
    ROUND(100.0 * (SUM(reached_cart) - SUM(reached_checkout)) / SUM(reached_cart), 1) as cart_abandon_pct,
    RANK() OVER (ORDER BY 100.0 * (SUM(reached_cart) - SUM(reached_checkout)) / SUM(reached_cart) DESC) as abandon_rank
FROM sessions
GROUP BY category
```

---

## Project Structure

```
nykaa-funnel-analysis/
│
├── nykaa_funnel_generator.ipynb   ← Full analysis notebook
├── nykaa_funnel_sessions.csv      ← Generated dataset (10K sessions)
├── nykaa_funnel.db                ← SQLite database for SQL queries
├── funnel_overall.png             ← Overall funnel chart
├── funnel_device.png              ← Conversion by device chart
├── funnel_category.png            ← Cart abandonment by category
└── README.md
```

---

## Dashboard

Built in Power BI with 5 visuals:
- KPI cards (Total Sessions, Total Orders, Overall Conversion Rate)
- Customer Purchase Funnel (7-stage horizontal bar)
- Cart Abandonment by Category
- Cart Adds by Category
- Conversion Rate by Device

<img width="1191" height="671" alt="Screenshot (390)" src="https://github.com/user-attachments/assets/657ce408-9603-4a1d-8a8b-ce46e4794648" />


---

## How to Run

```bash
# 1. Clone the repo
git clone https://github.com/yourusername/nykaa-funnel-analysis

# 2. Install dependencies
pip install pandas numpy matplotlib seaborn

# 3. Open notebook
jupyter notebook nykaa_funnel_generator.ipynb

# 4. Run all cells — dataset generates automatically, no download needed
```

---

## Business Impact Estimate

If Nykaa improved Add-to-Cart → Checkout conversion by just 10%:
- Additional checkouts per 10K sessions: ~60
- At avg order value of ₹800: **₹48,000 additional revenue per 10K sessions**
- At Nykaa's actual scale (millions of daily sessions): significant 8-figure annual impact

---

## What I Learned

- How to design realistic synthetic data that mirrors real business patterns
- SQL window functions (`RANK()`, `LAG()`) for funnel analysis
- How device type and product category interact with conversion — not just overall metrics
- How to connect data findings to specific, actionable business recommendations



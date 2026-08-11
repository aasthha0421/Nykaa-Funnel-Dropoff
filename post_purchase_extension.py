"""
Nykaa Funnel Project — Post-Purchase Extension
================================================
Extends the original purchase-funnel analysis (Homepage -> Order Placed)
with a post-purchase stage, to test a hypothesis drawn from real public
customer reviews: that the biggest revenue leak may not be pre-purchase
friction, but post-purchase failure (wrong/damaged items, delivery delays,
and refund/replacement refusals) — and that this leak is worse in
tier-2/3 cities, consistent with reports that a competitor (Purplle)
has a delivery-reliability edge there.

IMPORTANT — ALL DATA BELOW IS SYNTHETIC.
This does not use or represent real Nykaa order data. Probabilities are
illustrative assumptions designed to reflect the *direction* of patterns
seen in public reviews (PissedConsumer, Trustpilot), not measured real
rates. Every assumption is labeled in the ASSUMPTIONS block at the
bottom of this file. Treat this as a hypothesis-testing framework, not
a factual claim about Nykaa's actual operations.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
rng = np.random.default_rng(42)

# ---------------------------------------------------------------------
# 1. Generate synthetic post-purchase order data
#    (This zooms into the "Order Placed" stage of the original funnel
#    with a larger sample size, purely to make the risk-score patterns
#    visible — think of it as a separate, deeper-dive dataset.)
# ---------------------------------------------------------------------

N_ORDERS = 5000

# ASSUMPTION: city-tier mix among orders (not measured — a reasonable
# split reflecting India's e-commerce order distribution)
city_tier = rng.choice(
    ["metro", "tier2", "tier3"],
    size=N_ORDERS,
    p=[0.40, 0.35, 0.25]
)

category = rng.choice(
    ["skincare", "makeup", "haircare", "wellness"],
    size=N_ORDERS,
    p=[0.35, 0.30, 0.25, 0.10]
)

df = pd.DataFrame({
    "order_id": [f"NYK{100000+i}" for i in range(N_ORDERS)],
    "city_tier": city_tier,
    "category": category,
})

# ASSUMPTION: delivery delay probability is higher outside metros.
# Direction (tier3 > tier2 > metro) is based on the Purplle-vs-Nykaa
# tier-2/3 delivery reports found in research. Exact rates are illustrative.
delay_prob_map = {"metro": 0.10, "tier2": 0.18, "tier3": 0.27}
df["delivery_status"] = df["city_tier"].apply(
    lambda t: rng.choice(
        ["on_time", "delayed", "not_delivered"],
        p=[1 - delay_prob_map[t] - 0.03, delay_prob_map[t], 0.03]
    )
)

# ASSUMPTION: item-accuracy issue rate. Reviews repeatedly mention wrong
# or damaged items as a top complaint theme — baseline rate here is a
# deliberately conservative illustrative estimate, NOT a measured figure.
item_issue_prob = 0.12
df["item_accuracy"] = rng.choice(
    ["correct", "wrong_item", "damaged"],
    size=N_ORDERS,
    p=[1 - item_issue_prob, item_issue_prob * 0.6, item_issue_prob * 0.4]
)

# ASSUMPTION: resolution outcome, conditional on there being an issue.
# Reviews repeatedly described a "correct product was dispatched" denial
# pattern — modeled here as a meaningful share of "denied" outcomes,
# not a literal measured refund-denial rate.
def resolve(row):
    if row["item_accuracy"] == "correct" and row["delivery_status"] == "on_time":
        return "not_applicable"
    return rng.choice(
        ["refunded", "replaced", "denied", "unresolved"],
        p=[0.35, 0.25, 0.25, 0.15]
    )

df["resolution_outcome"] = df.apply(resolve, axis=1)

df["complaint_channel"] = rng.choice(
    ["app", "call", "email", "social", "none"],
    size=N_ORDERS,
    p=[0.30, 0.25, 0.20, 0.10, 0.15]
)

# ---------------------------------------------------------------------
# 2. Derived metric: Reorder-Risk Flag
#    High risk = item issue (wrong/damaged) AND resolution was denied
#    or left unresolved. This is the specific pattern that showed up
#    repeatedly in real review text.
# ---------------------------------------------------------------------
df["reorder_risk"] = (
    (df["item_accuracy"].isin(["wrong_item", "damaged"]))
    & (df["resolution_outcome"].isin(["denied", "unresolved"]))
).astype(int)

df["delivery_failure"] = (df["delivery_status"] != "on_time").astype(int)

# ---------------------------------------------------------------------
# 3. Analysis: does the hypothesis hold in this synthetic model?
# ---------------------------------------------------------------------
risk_by_tier = df.groupby("city_tier")["reorder_risk"].mean().reindex(
    ["metro", "tier2", "tier3"]
) * 100

delivery_fail_by_tier = df.groupby("city_tier")["delivery_failure"].mean().reindex(
    ["metro", "tier2", "tier3"]
) * 100

resolution_breakdown = (
    df[df["resolution_outcome"] != "not_applicable"]["resolution_outcome"]
    .value_counts(normalize=True) * 100
)

print("=" * 60)
print("REORDER-RISK RATE BY CITY TIER (%)")
print("=" * 60)
print(risk_by_tier.round(1))
print()
print("=" * 60)
print("DELIVERY FAILURE RATE BY CITY TIER (%)")
print("=" * 60)
print(delivery_fail_by_tier.round(1))
print()
print("=" * 60)
print("RESOLUTION OUTCOME BREAKDOWN, WHEN AN ISSUE OCCURRED (%)")
print("=" * 60)
print(resolution_breakdown.round(1))

# ---------------------------------------------------------------------
# 4. Charts
# ---------------------------------------------------------------------
fig, axes = plt.subplots(1, 3, figsize=(16, 5))

# Chart 1: Reorder-risk by city tier
sns.barplot(x=risk_by_tier.index, y=risk_by_tier.values, ax=axes[0],
            palette=["#2E86AB", "#F18F01", "#C73E1D"])
axes[0].set_title("Reorder-Risk Rate by City Tier\n(synthetic model)", fontsize=11)
axes[0].set_ylabel("% of orders")
axes[0].set_xlabel("")
for i, v in enumerate(risk_by_tier.values):
    axes[0].text(i, v + 0.3, f"{v:.1f}%", ha="center", fontweight="bold")

# Chart 2: Delivery failure by city tier
sns.barplot(x=delivery_fail_by_tier.index, y=delivery_fail_by_tier.values, ax=axes[1],
            palette=["#2E86AB", "#F18F01", "#C73E1D"])
axes[1].set_title("Delivery Failure Rate by City Tier\n(synthetic model)", fontsize=11)
axes[1].set_ylabel("% of orders")
axes[1].set_xlabel("")
for i, v in enumerate(delivery_fail_by_tier.values):
    axes[1].text(i, v + 0.5, f"{v:.1f}%", ha="center", fontweight="bold")

# Chart 3: Resolution outcome breakdown
colors = {"refunded": "#2E86AB", "replaced": "#4CAF50", "denied": "#C73E1D", "unresolved": "#999999"}
axes[2].pie(
    resolution_breakdown.values,
    labels=resolution_breakdown.index,
    autopct="%1.0f%%",
    colors=[colors.get(k, "#ccc") for k in resolution_breakdown.index],
    startangle=90
)
axes[2].set_title("Resolution Outcome When Item\nIssue Occurred (synthetic model)", fontsize=11)

plt.tight_layout()
plt.savefig("post_purchase_analysis.png", dpi=150, bbox_inches="tight")
print("\nSaved chart: post_purchase_analysis.png")

df.to_csv("post_purchase_orders.csv", index=False)
print("Saved dataset: post_purchase_orders.csv")

# ---------------------------------------------------------------------
# ASSUMPTIONS (fact-check before presenting)
# ---------------------------------------------------------------------
print("""
ASSUMPTIONS USED IN THIS MODEL (all illustrative, not measured):
1. City-tier order mix (40/35/25 metro/tier2/tier3) — a plausible split,
   not sourced from Nykaa data.
2. Delivery delay probabilities (10%/18%/27% by tier) — direction matches
   the tier-2/3 delivery-reliability gap reported vs. Purplle in public
   comparisons; exact percentages are assumed, not measured.
3. Item-accuracy issue rate (12% baseline) — reviews show wrong/damaged
   items as a recurring complaint theme, but no real rate was published;
   this figure is a deliberately conservative placeholder.
4. Resolution-outcome split (35% refunded / 25% replaced / 25% denied /
   15% unresolved) — modeled to reflect the "denied despite evidence"
   pattern seen repeatedly in review text, not a real published rate.
5. This dataset (N=5000) is separate from the original funnel dataset
   (N=10000 sessions, ~230 orders) — it zooms into the post-purchase
   stage with a larger sample purely to make patterns visible.
""")

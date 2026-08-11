import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_style("whitegrid")
rng = np.random.default_rng(42)

N_ORDERS = 5000

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

delay_prob_map = {"metro": 0.10, "tier2": 0.18, "tier3": 0.27}
df["delivery_status"] = df["city_tier"].apply(
    lambda t: rng.choice(
        ["on_time", "delayed", "not_delivered"],
        p=[1 - delay_prob_map[t] - 0.03, delay_prob_map[t], 0.03]
    )
)

item_issue_prob = 0.12
df["item_accuracy"] = rng.choice(
    ["correct", "wrong_item", "damaged"],
    size=N_ORDERS,
    p=[1 - item_issue_prob, item_issue_prob * 0.6, item_issue_prob * 0.4]
)

"---------------------------------------------------------------------------------"
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
df["reorder_risk"] = (
    (df["item_accuracy"].isin(["wrong_item", "damaged"]))
    & (df["resolution_outcome"].isin(["denied", "unresolved"]))
).astype(int)

df["delivery_failure"] = (df["delivery_status"] != "on_time").astype(int)

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
print("""

   (N=10000 sessions, ~230 orders) — it zooms into the post-purchase
   stage with a larger sample purely to make patterns visible.
""")

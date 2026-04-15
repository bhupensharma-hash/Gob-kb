# OSA → PSL Causal Link

## What this captures

This atom documents the **causal mechanism** by which on-shelf availability
(OSA) drives potential sales loss (PSL). Both atoms exist independently
(`metrics.osa`, `metrics.psl`); this atom captures the *relationship between
them* — direction, mechanism, elasticity, and confidence — in a form that
playbooks and reports can compose into narratives.

## Direction

A **decrease** in OSA causes an **increase** in PSL. The relationship is
monotonic within the working OSA range (50–95%).

## Mechanism

When a SKU is out of stock at a store, customers who arrive intending to
purchase it cannot do so. Some fraction of those customers:

1. **Substitute** to another SKU (within own brand or to a competitor) — no
   PSL realized at the brand level if substitution is intra-brand
2. **Defer** the purchase to another visit — recoverable revenue, delayed
3. **Abandon** the purchase entirely — true revenue loss

PSL captures the third category by approximation: it assumes the forecast
demand × stockout-time × price represents the maximum potential loss, before
adjusting for substitution.

## Elasticity (rule of thumb)

For most quick-commerce SKUs:

```
ΔPSL_per_day ≈ daily_demand × price × ΔOSA_fraction
```

So for a SKU with 100 units/day forecast demand at ₹200/unit, dropping OSA
from 85% to 68% (a 17pp = 0.17 fraction shift) costs roughly:

```
100 × 200 × 0.17 = ₹3,400/day per affected store-SKU
```

Aggregated across stores and SKUs, this is the headline PSL number reported
in chat replies and report sections.

## Confidence: high

This relationship is well-established across categories. The formula is
directionally accurate for the working OSA range. Specific elasticity
multipliers vary by category (perishables higher; staples lower) — see the
caveats list in `_node.yaml`.

## Caveats (when the relationship breaks down)

1. **Intra-brand substitution.** If your other SKUs in the same category and
   same store ARE in stock, customers may switch to them. Realized brand-level
   PSL is then lower than computed. Cross-check with own-brand category share
   in the affected stores.

2. **Demand suppression at chronic low OSA.** Below 50% OSA sustained for >2
   weeks, customers stop attempting to purchase the SKU at that store. Forecast
   demand becomes downward-biased, and the PSL formula under-reports true loss.

3. **Festival amplification.** During Diwali corridor and other peak-demand
   weeks, daily_demand can spike 2-4×, and elasticity is 1.5-3× baseline.

## How chat uses this

When a user asks *"how much would I recover by fixing OSA?"*, the planner
picks this atom. The chat assembler renders the elasticity and the LLM
multiplies it by the user's specific gap to produce a recovery estimate.

## How report uses this

The availability section's playbook adds a `render` step pointing to this
atom after the diagnostic. The rendered paragraph quantifies the recovery
opportunity in the report narrative — closing the loop from "what's wrong"
to "what it costs."

## How playbooks use this

A playbook step `traverse_causes from: metrics.osa to: metrics.market_share`
walks the causal chain through this atom (and through
`metric_relationships.psl_drives_share_loss` if/when authored). Each link
contributes a paragraph to the rendered output.

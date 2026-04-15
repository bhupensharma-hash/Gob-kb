# Potential Sales Loss (PSL)

## Definition

PSL = the estimated revenue (in ₹) that a SKU would have generated at a store
during the periods it was unavailable, given that store's expected demand.

It is the dollar-translation of OSA gaps — used to prioritize *which* OSA
problems are worth fixing.

## Formula (store-day grain)

```
psl_mrp = (forecast_daily_consumption - actual_inventory) * price
         when forecast_daily_consumption > actual_inventory
         else 0
```

In SQL form, against the attribution tables:

```sql
SUM(CASE
    WHEN fin_cpd > total_inv
    THEN (fin_cpd - total_inv) * price
    ELSE 0
END) AS psl_mrp
```

Where:
- `fin_cpd` — finalized consumption per day (forecasted demand)
- `total_inv` — total inventory at the store
- `price` — selling price

## Variants

| Variant | Use case |
|---|---|
| `psl_mrp` | Daily potential sales loss |
| `psl_mrp_listed` | PSL only across stores where the SKU is listed |
| `psl_mrp_listed_7d` | 7-day extrapolation: `psl_mrp_listed * 7` |

## Materiality filters

For surfacing in reports and chat, apply:

- Item-level: `psl_mrp > ₹100` (filter noise)
- Aggregate: total PSL `> ₹5,000` per segment

Anything below these thresholds is statistical noise, not an actionable problem.

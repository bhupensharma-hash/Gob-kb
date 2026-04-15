# OSA Health Benchmark

## Bands

| Band | Range | Color | Action |
|---|---|---|---|
| **Healthy** | OSA ≥ 90% | Green | No action needed |
| **Warning** | 80% ≤ OSA < 90% | Amber | Investigate within a week |
| **Critical** | OSA < 80% | Red | Immediate attention |

## Category-specific overrides

These bands are reasonable defaults for shelf-stable FMCG. Some categories
warrant tighter or looser bands due to supply-chain or category economics:

| Category | Healthy floor | Reason |
|---|---|---|
| Ghee | 85% | Shelf-stable, high margin, easier to keep in stock |
| Paneer | 70% | Perishable, cold-chain risk |
| Milk | 80% | Daily replenishment cycle |
| Makhana | 80% | Emerging category, high discounting phase |

## Interpretation rules

- Always use **weighted OSA**, not raw OSA, when classifying.
- Compare to category benchmark, not just the absolute band — a 78% OSA in
  paneer is fine; in ghee it's a problem.
- Sustained warning (4+ weeks at 80-90%) is a bigger signal than a single
  critical week — chronic gaps compound into share loss.

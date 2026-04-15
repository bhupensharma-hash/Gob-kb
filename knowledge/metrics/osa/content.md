# On-Shelf Availability (OSA)

## Definition

OSA = the percentage of times a SKU is found in stock across the stores where
it is listed. It is the single biggest controllable lever on q-commerce revenue.

## Formula

```sql
weighted_osa = SUM(total_available * estimated_offtake)
             / NULLIF(SUM(total_scrapes * estimated_offtake), 0)
```

## Variants

| Variant | Definition | When to use |
|---|---|---|
| **Weighted OSA** | Availability % weighted by estimated offtake | Default — reflects revenue impact, not raw count |
| **Raw OSA** | total_available / total_scrapes | Diagnostic only — over-weights low-volume stores |
| **OSA on Listed Stores** | available / scrapes, only across stores that listed the SKU in the last 14 days | Use when distinguishing distribution gaps from in-store stockouts |

## Source columns

From `qcom_pid_metrics` (and platform-specific variants):
- `total_available` — count of times the SKU was available across scrapes
- `total_scrapes` — count of times the scraper checked
- `estimated_offtake_mrp_*` — for the weighting factor

## Common pitfalls

- **Pooling across platforms** — OSA must be computed per platform, not pooled.
  Aggregating raw `total_available` across Blinkit + Instamart + Zepto produces
  meaningless numbers.
- **Ignoring listing context** — A SKU with 60% OSA across all stores might be
  100% OSA on the stores that listed it, with the gap being a distribution
  problem, not an availability problem. Cross-check via OSA on Listed Stores.
- **Ignoring weighting** — Raw OSA over-weights small stores. Always prefer
  weighted OSA for revenue-relevant decisions.

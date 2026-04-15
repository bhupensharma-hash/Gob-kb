# Transfer Issue Detection

## What it identifies

A **transfer issue** is when inventory exists in the backend warehouse but is
not reaching frontend dark store shelves. The brand has procured stock and the
platform warehouse received it, but last-mile transfer from warehouse to store
is failing. Revenue loss is **entirely preventable** because the inventory
exists — it's an execution problem, not a supply problem.

## Detection conditions (all three must be true)

1. **Backend has inventory:**
   `backend_doi > LEAST(5, doi_th * 0.75)`
2. **Frontend is out of stock:**
   `osa_listing < 70%`
3. **There is real revenue loss:**
   `psl_mrp_listed > 0`

When all three are true simultaneously, the SKU is classified as a transfer issue.

## Threshold formula explained

The backend DOI threshold uses `LEAST(5, doi_th * 0.75)` because:

- `doi_th = min(5, PO_cycle/2 + TAT/2)` — the dynamic threshold accounting for
  this SKU's lead time
- We multiply by 0.75 to require a clear safety margin (not just "barely above
  threshold")
- We cap at 5 days because beyond that, even good lead times don't justify
  prolonged backend stock without frontend availability

## Loss extrapolation

The 7-day loss is a simple extrapolation: `psl_mrp_listed_7d = psl_mrp_listed * 7`.

This is appropriate because transfer issues persist until explicitly resolved —
they don't self-correct like some PO-timing issues.

## Ownership

- **Owned by:** Platform ops / dark store operations team
- **NOT owned by:** Brand procurement (they already did their job)
- **Resolution:** Escalate to the platform's warehouse operations team

## Typical root causes

- Dark store capacity constraints
- Internal transfer scheduling gaps
- Damaged inventory quarantined in backend
- System mismatches between backend and frontend inventory counts

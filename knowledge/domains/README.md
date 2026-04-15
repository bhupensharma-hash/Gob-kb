# domains/

This is where GoBIQ's existing typed-domain content lives. Migrate the contents
of `backend/app/ai/knowledge/domains/` from the GoBIQ repo into this folder
during Phase 0 of the migration.

Expected children (after migration):

- `brand_growth/` — availability_gap, city_breakdown, competitive_context, efficiency_check, new_launch_tracker, sku_performance
- `supply_chain/` — transfer_issues, missing_po, fill_rate_issues, delivery_time_issues, excess_inventory, suggest_po, prioritise_po
- `locality_metrics/` — locality_availability, store_health, platform_nuances, pricing_intelligence, psl_impact
- `keyword_visibility/` — search_performance, keyword_optimization, ad_spend_roas, availability_in_search

Each domain is a folder with `_node.yaml` (type: `domain`) + `content.md`.
Each topic under a domain is a folder with `_node.yaml` (type: `topic`) + `content.md`.

See [`/CONTRIBUTING.md`](../../CONTRIBUTING.md) for the authoring contract.

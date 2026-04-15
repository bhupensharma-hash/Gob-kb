# templates/

Chat-layer templates — Layer 0+1 shapes for specific question patterns.
Used by the chat assembler when the planner picks a template node.

## Existing templates (after migration from GoBIQ)

- `growth_diagnosis/` — for "why is my growth/decline X" questions
- `competitive_intelligence/` — for "what are competitors doing" questions

Each template is a folder with `_node.yaml` (type: `template`) + `content.md`.
The `content.md` defines the trigger queries, analyst mindset, Layer 0+1
structure, and Layer 2 deep-dive paths.

See [`/docs/content_types.md`](../../docs/content_types.md) for the template
content contract.

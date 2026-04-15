# Availability Diagnosis Procedure

## Mindset

You are a doctor running a diagnosis. The user has a symptom (OSA dropped).
Your job is to trace from symptom to root cause — not just restate the symptom
with more numbers.

Work the tree top-down: split listing vs inventory first, then narrow.

## The decision tree (high level)

```
OSA dropped
│
├── Did DS_listing drop > 10%?
│   │
│   ├── YES → Case 1: Listing Issue
│   │         ├── 1A: warehouse stock exists but not transferred
│   │         └── 1B: PO problem (no PO, late PO, low fill)
│   │
│   └── NO  → Case 2: Inventory Issue
│             ├── 2A: transfer issue (backend full, frontend empty)
│             └── 2B: supply shortage (backend_doi < threshold)
```

## How chat consumes this

The chat assembler walks **one step per turn**. After each step that involves
data, the assembler renders Layer 0+1 and offers follow-up paths corresponding
to the next 2-3 steps in the traversal.

## How report consumes this

The report assembler walks **all steps in sequence**, rendering each into a
sub-section of the availability report section. See
`output_specs.availability_section`.

## Status

This is a **starter** procedure. The full Case 1 sub-tree
(`procedures.availability_diagnosis_listing_branch`) and the PO/fill-rate
sub-trees are placeholder references — to be added during migration of
strategy-agent-core's `availability_deep_dive.md` into atomic form.

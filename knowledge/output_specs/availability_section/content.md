# Availability Report Section — Spec

This `output_spec` defines how the availability section appears in any report
that includes it (MBR, Category Analysis, on-demand availability deep-dive).

## Composition

The section is composed of one or more procedure walks. Each procedure walk
becomes a sub-section in the rendered HTML.

## Style guide for this section

- **Headline first.** Lead with the OSA delta and the root cause, not a chart.
- **Numbers must include change + benchmark.** "OSA = 76%" is data; "OSA dropped 17pp to 76% (critical band)" is insight.
- **Owner must be named.** Every action needs a "this team owns it" line.
- **No methodology callouts.** Don't tell the reader how PSL is computed in the
  body — that lives in the concept atom and is rendered in an appendix if needed.

## Render flow

```
output_specs.availability_section
   └── walks → procedures.availability_diagnosis
       ├── renders concepts.osa
       ├── fetches OSA + listing deltas (via consumer's data_fetcher)
       ├── branches on listing drop
       ├── if inventory branch → runs detections.transfer_issue
       └── terminates with verdict template
```

The report assembler consumes this spec. The chat assembler ignores
`output_spec` atoms entirely (chat walks procedures directly, not via specs).

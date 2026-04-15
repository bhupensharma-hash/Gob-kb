# Availability Report Section — Spec

This `report_section` defines how the availability section appears in any report
that includes it (MBR, Category Analysis, on-demand availability deep-dive).

## Composition

The section is composed of one or more playbook walks. Each playbook walk
becomes a sub-section in the rendered HTML.

## Style guide for this section

- **Headline first.** Lead with the OSA delta and the root cause, not a chart.
- **Numbers must include change + benchmark.** "OSA = 76%" is data; "OSA dropped 17pp to 76% (critical band)" is insight.
- **Owner must be named.** Every action needs a "this team owns it" line.
- **No methodology callouts.** Don't tell the reader how PSL is computed in the
  body — that lives in the metric atom and is rendered in an appendix if needed.

## Render flow

```
report_sections.availability_section
   └── walks → playbooks.availability_diagnosis
       ├── renders metrics.osa
       ├── fetches OSA + listing deltas (via consumer's data_fetcher)
       ├── branches on listing drop
       ├── if inventory branch → runs diagnostics.transfer_issue
       └── terminates with verdict template
```

The report assembler consumes this spec. The chat assembler ignores
`report_section` atoms entirely (chat walks playbooks directly, not via specs).

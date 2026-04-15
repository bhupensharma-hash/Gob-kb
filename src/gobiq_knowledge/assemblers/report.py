"""
Report assembler — depth-N walk that executes a report_section into a rendered report.

Given a report_section_id, this:
  1. Loads the report_section atom (defines section order + playbook references)
  2. For each section, walks the referenced playbook's traversal end-to-end
  3. Composes atom contents into HTML using the referenced CSS framework atom
  4. Returns the assembled HTML string

This is the missing half that GoBIQ chat doesn't have today. It lets the
SAME knowledge graph drive batch report generation in addition to chat.

Design note: data execution (running SQL, fetching from Excel) is left to the
consuming app. This assembler returns a structured report tree; the consumer
plugs in real values where the playbook says `fetch_data` or `run_diagnostic`.

This module ships a SKELETON. Replace the stub renderers with real
implementations as you migrate report sections from strategy-agent-core.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional

from ..loader import KnowledgeGraph, KnowledgeNode

logger = logging.getLogger(__name__)


# Type alias for the data-fetch callback the consumer must supply.
# Given a recipe action string or SQL fragment, returns whatever data the tool produced.
DataFetcher = Callable[[str], Any]


@dataclass
class RenderedSection:
    """One rendered section in the assembled report."""

    section_id: str
    title: str
    html: str
    sub_sections: List["RenderedSection"] = field(default_factory=list)


@dataclass
class AssembledReport:
    """The full report, ready to serialize to HTML/PDF."""

    report_section_id: str
    title: str
    sections: List[RenderedSection]
    css: str

    def to_html(self) -> str:
        """Render the assembled report tree to a single HTML document."""
        body_blocks = []
        for section in self.sections:
            body_blocks.append(_render_section_html(section))
        body = "\n".join(body_blocks)
        return (
            "<!doctype html><html><head>"
            f"<title>{_escape(self.title)}</title>"
            f"<style>{self.css}</style>"
            "</head><body>"
            f"{body}"
            "</body></html>"
        )


def assemble_report(
    graph: KnowledgeGraph,
    report_section_id: str,
    data_fetcher: Optional[DataFetcher] = None,
) -> AssembledReport:
    """
    Assemble a report by walking a report_section through its referenced playbooks.

    Args:
        graph: A loaded KnowledgeGraph.
        report_section_id: The dot-path ID of the report_section atom.
        data_fetcher: Callback invoked for traversal steps that need real data
                      (run_diagnostic, fetch_data). Required for production reports.

    Returns:
        An AssembledReport ready to render as HTML.
    """
    spec = graph.get_node(report_section_id)
    if not spec:
        raise ValueError(f"Unknown report_section: {report_section_id}")
    if spec.type != "report_section":
        raise ValueError(
            f"Node {report_section_id} is type '{spec.type}', expected 'report_section'"
        )

    # Resolve CSS framework if referenced
    css = _resolve_css(graph, spec)

    sections: List[RenderedSection] = []
    for section_def in spec.sections:
        rendered = _render_section(graph, section_def, data_fetcher)
        if rendered:
            sections.append(rendered)

    return AssembledReport(
        report_section_id=report_section_id,
        title=spec.name,
        sections=sections,
        css=css,
    )


# ---------------------------------------------------------------------- #
# Internals
# ---------------------------------------------------------------------- #

def _resolve_css(graph: KnowledgeGraph, spec: KnowledgeNode) -> str:
    """Pull CSS from the report_section's `uses_template` related-edge if present."""
    for rel in spec.related:
        if rel.get("relation") == "uses_template":
            css_node = graph.get_node(rel.get("id", ""))
            if css_node and css_node.type == "report_section":
                return graph.get_content(css_node.id)
    return ""


def _render_section(
    graph: KnowledgeGraph,
    section_def: Dict[str, Any],
    data_fetcher: Optional[DataFetcher],
) -> Optional[RenderedSection]:
    """Render one section by walking its referenced playbook."""
    section_id = section_def.get("id", "unnamed_section")
    title = section_def.get("title", section_id)
    playbook_id = section_def.get("playbook")

    if not playbook_id:
        return RenderedSection(
            section_id=section_id,
            title=title,
            html=f"<section><h2>{_escape(title)}</h2></section>",
        )

    playbook = graph.get_node(playbook_id)
    if not playbook or playbook.type != "playbook":
        logger.warning(
            "Section %s references missing playbook %s", section_id, playbook_id
        )
        return None

    # Walk the playbook's traversal.
    body_blocks: List[str] = []
    for step in playbook.traversal:
        block = _execute_step(graph, step, data_fetcher)
        if block:
            body_blocks.append(block)

    body_html = "\n".join(body_blocks)
    return RenderedSection(
        section_id=section_id,
        title=title,
        html=f"<section><h2>{_escape(title)}</h2>\n{body_html}\n</section>",
    )


def _execute_step(
    graph: KnowledgeGraph,
    step: Dict[str, Any],
    data_fetcher: Optional[DataFetcher],
) -> str:
    """
    Execute one traversal step. Returns an HTML fragment.

    Step types (from knowledge/_schema.yaml traversal_step_types):
      - run_diagnostic: Execute a diagnostic rule (returns true/false)
      - fetch_data: Run a recipe to fetch data
      - branch: if/else based on a condition
      - render: Render a metric / diagnostic / benchmark into output
      - call_playbook: Recursively call another playbook
      - traverse_causes: Walk the causal graph from `from:` metric to `to:` metric,
                         rendering each metric_relationship link along the path
      - terminate: End the traversal
    """
    step_type = step.get("step")
    target_id = step.get("ref")

    if step_type == "render":
        target = graph.get_node(target_id) if target_id else None
        if target:
            content = graph.get_content(target_id)
            return f"<div class='atom-{target.type}'><h3>{_escape(target.name)}</h3>\n{_md_to_html(content)}\n</div>"
        return ""

    if step_type == "run_diagnostic" and data_fetcher:
        target = graph.get_node(target_id) if target_id else None
        if target and target.sql:
            try:
                result = data_fetcher(target.sql)
                return f"<div class='diagnostic-result'>{_escape(str(result))}</div>"
            except Exception as exc:
                logger.error("Data fetch failed for %s: %s", target_id, exc)
        return ""

    if step_type == "fetch_data" and data_fetcher:
        action = step.get("action", "")
        try:
            result = data_fetcher(action)
            return f"<div class='data-result'>{_escape(str(result))}</div>"
        except Exception as exc:
            logger.error("Data fetch failed: %s", exc)
        return ""

    if step_type == "call_playbook":
        sub = graph.get_node(target_id) if target_id else None
        if sub and sub.type == "playbook":
            sub_blocks = [
                _execute_step(graph, s, data_fetcher) for s in sub.traversal
            ]
            return "\n".join(b for b in sub_blocks if b)
        return ""

    if step_type == "branch":
        # Branches are evaluated by the data_fetcher; the assembler just renders both arms when no fetcher is present.
        # In production, the fetcher should evaluate the condition and the assembler picks the matching arm.
        return ""

    if step_type == "traverse_causes":
        return _render_causal_path(graph, step)

    if step_type == "terminate":
        return ""

    return ""


def _render_causal_path(graph: KnowledgeGraph, step: Dict[str, Any]) -> str:
    """
    Walk the causal graph from `from:` metric to `to:` metric, rendering each
    metric_relationship link along the path.

    Strategy:
      1. BFS from `from_id`, following `causes` edges on metric atoms.
      2. For each (source, target) edge along the path, look up a
         `metric_relationship` atom whose source_metric/target_metric match.
      3. Render each found relationship atom as an HTML block.
    """
    from_id = step.get("from")
    to_id = step.get("to")
    render_each = step.get("render_each_link", True)
    max_depth = step.get("max_depth", 5)

    if not from_id:
        return ""

    # Build adjacency by 'causes' edges out of metric atoms.
    causes_adj: Dict[str, List[str]] = {}
    for node in graph.all_nodes():
        if node.type != "metric":
            continue
        for rel in node.related:
            if rel.get("relation") == "causes":
                target = rel.get("id")
                if target:
                    causes_adj.setdefault(node.id, []).append(target)

    # Also include implicit chain via metric_relationship atoms:
    # metric_relationship's source_metric → target_metric is a 'causes' edge.
    for mr in graph.list_nodes(type_filter="metric_relationship"):
        s = mr.source_metric
        t = mr.target_metric
        if s and t:
            adj = causes_adj.setdefault(s, [])
            if t not in adj:
                adj.append(t)

    # BFS to find a path
    if to_id is None:
        # Walk all reachable nodes up to max_depth, emit edges in BFS order
        path_edges: List[tuple] = []
        visited = {from_id}
        frontier = [from_id]
        depth = 0
        while frontier and depth < max_depth:
            next_frontier = []
            for n in frontier:
                for child in causes_adj.get(n, []):
                    if child not in visited:
                        path_edges.append((n, child))
                        visited.add(child)
                        next_frontier.append(child)
            frontier = next_frontier
            depth += 1
    else:
        # BFS to a specific target
        parents: Dict[str, str] = {from_id: ""}
        frontier = [from_id]
        depth = 0
        while frontier and depth < max_depth and to_id not in parents:
            next_frontier = []
            for n in frontier:
                for child in causes_adj.get(n, []):
                    if child not in parents:
                        parents[child] = n
                        next_frontier.append(child)
            frontier = next_frontier
            depth += 1
        # Reconstruct path
        path_edges = []
        if to_id in parents:
            cur = to_id
            while parents.get(cur):
                path_edges.append((parents[cur], cur))
                cur = parents[cur]
            path_edges.reverse()

    if not path_edges:
        return f"<div class='causal-path empty'>No causal path from {_escape(from_id)} to {_escape(to_id or '?')}.</div>"

    # Render each edge by finding the matching metric_relationship atom (if any)
    blocks: List[str] = []
    for source, target in path_edges:
        relationship = _find_relationship_atom(graph, source, target)
        if relationship and render_each:
            content = graph.get_content(relationship.id)
            blocks.append(
                f"<div class='atom-metric_relationship'>"
                f"<h3>{_escape(relationship.name)}</h3>"
                f"<p><strong>{_escape(relationship.mechanism_short or '')}</strong></p>"
                f"<p>Elasticity: {_escape(relationship.elasticity or 'n/a')}</p>"
                f"{_md_to_html(content)}"
                f"</div>"
            )
        else:
            # No formal relationship atom — render a stub edge
            src = graph.get_node(source)
            tgt = graph.get_node(target)
            blocks.append(
                f"<div class='causal-edge stub'>"
                f"{_escape(src.name if src else source)} → "
                f"{_escape(tgt.name if tgt else target)}"
                f"</div>"
            )
    return "\n".join(blocks)


def _find_relationship_atom(graph: KnowledgeGraph, source_id: str, target_id: str) -> Optional[KnowledgeNode]:
    """Find a metric_relationship atom whose source_metric/target_metric match."""
    for mr in graph.list_nodes(type_filter="metric_relationship"):
        if mr.source_metric == source_id and mr.target_metric == target_id:
            return mr
    return None


def _render_section_html(section: RenderedSection) -> str:
    sub_html = "\n".join(_render_section_html(s) for s in section.sub_sections)
    return section.html + ("\n" + sub_html if sub_html else "")


def _md_to_html(md: str) -> str:
    """Minimal markdown→HTML stub. Replace with markdown-it or similar in production."""
    if not md:
        return ""
    # Just wrap in <pre> for now — the consuming app should do real markdown conversion.
    return f"<pre>{_escape(md)}</pre>"


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
            .replace('"', "&quot;")
    )


__all__ = ["assemble_report", "AssembledReport", "RenderedSection", "DataFetcher"]

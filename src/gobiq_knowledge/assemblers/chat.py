"""
Chat assembler — depth-1 retrieval for the GoBIQ chat planner.

Given a node_id, returns a context blob containing:
  1. Global narration rules (always)
  2. Parent chain content (walked up to root)
  3. The requested node's content
  4. Related-nodes summary (names + descriptions + relation type)

This mirrors GoBIQ's existing get_retrieval_context() so that swapping in
this package is behavior-preserving for chat.
"""

from __future__ import annotations

from typing import List

from ..loader import KnowledgeGraph


def assemble_chat_context(graph: KnowledgeGraph, node_id: str) -> str:
    """
    Build the full context string for a planner retrieval call.

    Args:
        graph: A loaded KnowledgeGraph.
        node_id: The dot-path ID of the target node.

    Returns:
        A formatted context string suitable for inclusion in an LLM prompt.
    """
    node = graph.get_node(node_id)
    if not node:
        return f"Unknown knowledge node: {node_id}"

    sections: List[str] = []

    # 1. Global narration rules
    if graph.global_content:
        sections.append("## NARRATION_RULES\n\n" + graph.global_content)

    # 2. Parent chain content (walk up to root, render in root→leaf order)
    parent_blocks: List[str] = []
    current_id = node.parent
    while current_id:
        parent = graph.get_node(current_id)
        if not parent:
            break
        parent_content = graph.get_content(current_id)
        if parent_content:
            parent_blocks.append(
                f"## {parent.name.upper()}_GLOBAL_RULES\n\n{parent_content}"
            )
        current_id = parent.parent
    sections.extend(reversed(parent_blocks))

    # 3. Requested node content
    node_content = graph.get_content(node_id)
    if node_content:
        section_name = node.name.upper().replace(" ", "_")
        sections.append(f"## {section_name}\n\n{node_content}")
    elif node.children:
        # Node has no own content; summarize its children instead.
        child_summaries: List[str] = []
        for child_id in node.children:
            child = graph.get_node(child_id)
            if child:
                child_summaries.append(f"- **{child.name}**: {child.description}")
        if child_summaries:
            sections.append(
                f"## {node.name.upper()} — Available Topics\n\n"
                + "\n".join(child_summaries)
            )

    # 4. Related nodes summary
    if node.related:
        related_lines: List[str] = []
        for rel in node.related:
            rel_node = graph.get_node(rel.get("id", ""))
            if rel_node:
                related_lines.append(
                    f"- **{rel_node.name}** ({rel.get('relation', 'related')}): "
                    f"{rel.get('label', rel_node.description)}"
                )
        if related_lines:
            sections.append("## RELATED_KNOWLEDGE\n\n" + "\n".join(related_lines))

    return "\n\n---\n\n".join(sections) if sections else "No content available."


__all__ = ["assemble_chat_context"]

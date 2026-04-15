"""
gobiq-knowledge — single source of truth for GoBIQ analytical knowledge.

Public API:

    from gobiq_knowledge import load
    from gobiq_knowledge.assemblers.chat import assemble_chat_context
    from gobiq_knowledge.assemblers.report import assemble_report

    graph = load()
    chat_blob = assemble_chat_context(graph, node_id="domains.supply_chain.transfer_issues")
    html = assemble_report(graph, report_section_id="report_sections.availability_section")
"""

from pathlib import Path
from typing import Optional

from .loader import KnowledgeGraph, KnowledgeNode

__version__ = "0.3.0"

_DEFAULT_KNOWLEDGE_ROOT = Path(__file__).resolve().parent.parent.parent / "knowledge"

_cached_graph: Optional[KnowledgeGraph] = None


def load(root_path: Optional[Path] = None, force_reload: bool = False) -> KnowledgeGraph:
    """
    Load (and cache) the knowledge graph.

    Args:
        root_path: Path to the knowledge/ directory. Defaults to the bundled tree.
        force_reload: If True, re-read all files even if a cached graph exists.

    Returns:
        A populated KnowledgeGraph.
    """
    global _cached_graph

    if _cached_graph is not None and not force_reload:
        return _cached_graph

    root = Path(root_path) if root_path else _DEFAULT_KNOWLEDGE_ROOT
    graph = KnowledgeGraph(root_path=str(root))
    graph.load()
    _cached_graph = graph
    return graph


__all__ = ["load", "KnowledgeGraph", "KnowledgeNode", "__version__"]

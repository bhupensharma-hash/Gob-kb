"""
Knowledge Graph Loader — builds an in-memory graph from the file-system knowledge tree.

Walks the knowledge/ directory, finds all _node.yaml files, parses them into
KnowledgeNode objects, validates references, and exposes methods for retrieval.

Originally lifted from GoBIQ's backend/app/ai/knowledge/loader.py and extended
with new atom types (metric, diagnostic, benchmark, playbook, report_section).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional

import yaml

logger = logging.getLogger(__name__)


# Atom types recognized by the loader. Must match knowledge/_schema.yaml.
VALID_NODE_TYPES = {
    # Existing GoBIQ types:
    "global",
    "category",
    "chat_template",
    "domain",
    "topic",
    # Option B taxonomy:
    "metric",
    "metric_relationship",
    "diagnostic",
    "benchmark",
    "playbook",
    "report_section",
}


@dataclass
class KnowledgeNode:
    """A single atom in the knowledge graph."""

    id: str
    name: str
    description: str
    type: str
    parent: Optional[str]
    children: List[str] = field(default_factory=list)
    related: List[dict] = field(default_factory=list)
    primitives: List[str] = field(default_factory=list)
    common_questions: List[str] = field(default_factory=list)
    planner_hint: str = ""
    expose_to_planner: bool = False

    # Type-specific fields:
    traversal: List[dict] = field(default_factory=list)   # playbook
    sql: Optional[str] = None                              # diagnostic
    thresholds: List[dict] = field(default_factory=list)   # benchmark
    sections: List[dict] = field(default_factory=list)     # report_section

    # metric_relationship-specific:
    source_metric: Optional[str] = None
    target_metric: Optional[str] = None
    direction: Optional[str] = None
    mechanism_short: Optional[str] = None
    elasticity: Optional[str] = None
    confidence: Optional[str] = None
    caveats: List[str] = field(default_factory=list)

    # metric / metric_relationship — explicit math when applicable:
    formula: Optional[str] = None

    # metric — list of input metrics this is computed from:
    derives_from: List[dict] = field(default_factory=list)

    content_path: Optional[Path] = None


class KnowledgeGraph:
    """In-memory knowledge graph built from the file-system tree."""

    def __init__(self, root_path: str):
        self._nodes: Dict[str, KnowledgeNode] = {}
        self._root_path = Path(root_path)
        self._global_content: Optional[str] = None

    # ------------------------------------------------------------------ #
    # Loading
    # ------------------------------------------------------------------ #

    def load(self) -> None:
        """Walk the tree, read _node.yaml files, build the in-memory graph."""
        self._nodes.clear()
        self._global_content = None

        node_files = sorted(self._root_path.rglob("_node.yaml"))
        if not node_files:
            logger.warning("No _node.yaml files found under %s", self._root_path)
            return

        for node_file in node_files:
            try:
                with open(node_file, "r") as f:
                    data = yaml.safe_load(f)
                if not data or "id" not in data:
                    logger.warning("Skipping invalid node file: %s", node_file)
                    continue

                content_path = node_file.parent / "content.md"
                node = KnowledgeNode(
                    id=data["id"],
                    name=data.get("name", ""),
                    description=data.get("description", ""),
                    type=data.get("type", "topic"),
                    parent=data.get("parent"),
                    children=data.get("children", []),
                    related=data.get("related", []),
                    primitives=data.get("primitives", []),
                    common_questions=data.get("common_questions", []),
                    planner_hint=data.get("planner_hint", ""),
                    expose_to_planner=data.get("expose_to_planner", False),
                    traversal=data.get("traversal", []),
                    sql=data.get("sql"),
                    thresholds=data.get("thresholds", []),
                    sections=data.get("sections", []),
                    source_metric=data.get("source_metric"),
                    target_metric=data.get("target_metric"),
                    direction=data.get("direction"),
                    mechanism_short=data.get("mechanism_short"),
                    elasticity=data.get("elasticity"),
                    confidence=data.get("confidence"),
                    caveats=data.get("caveats", []),
                    formula=data.get("formula"),
                    derives_from=data.get("derives_from", []),
                    content_path=content_path if content_path.exists() else None,
                )
                self._nodes[node.id] = node

                if node.type == "global" and node.content_path:
                    # Concatenate all global content (multiple global atoms allowed).
                    block = node.content_path.read_text(encoding="utf-8")
                    self._global_content = (
                        f"{self._global_content}\n\n{block}"
                        if self._global_content
                        else block
                    )

            except Exception as exc:
                logger.error("Failed to load node from %s: %s", node_file, exc)

        self._validate()
        logger.info(
            "Knowledge graph loaded: %d nodes (%d exposed to planner)",
            len(self._nodes),
            sum(1 for n in self._nodes.values() if n.expose_to_planner),
        )

    # ------------------------------------------------------------------ #
    # Validation (also runs in tests/test_references.py for CI)
    # ------------------------------------------------------------------ #

    def _validate(self) -> None:
        for node_id, node in self._nodes.items():
            if node.type not in VALID_NODE_TYPES:
                logger.warning(
                    "Node '%s' has unknown type '%s'", node_id, node.type
                )
            if node.parent and node.parent not in self._nodes:
                logger.warning(
                    "Node '%s' references unknown parent '%s'", node_id, node.parent
                )
            for child_id in node.children:
                if child_id not in self._nodes:
                    logger.warning(
                        "Node '%s' references unknown child '%s'", node_id, child_id
                    )
            for rel in node.related:
                rel_id = rel.get("id", "")
                if rel_id and rel_id not in self._nodes:
                    logger.warning(
                        "Node '%s' references unknown related node '%s'",
                        node_id,
                        rel_id,
                    )

    # ------------------------------------------------------------------ #
    # Node access
    # ------------------------------------------------------------------ #

    def get_node(self, node_id: str) -> Optional[KnowledgeNode]:
        return self._nodes.get(node_id)

    def get_content(self, node_id: str) -> str:
        node = self._nodes.get(node_id)
        if not node or not node.content_path:
            return ""
        try:
            return node.content_path.read_text(encoding="utf-8")
        except Exception as exc:
            logger.error("Failed to read content for '%s': %s", node_id, exc)
            return ""

    def all_nodes(self) -> List[KnowledgeNode]:
        return list(self._nodes.values())

    def list_nodes(
        self,
        type_filter: Optional[str] = None,
        primitive_filter: Optional[str] = None,
    ) -> List[KnowledgeNode]:
        result = list(self._nodes.values())
        if type_filter:
            result = [n for n in result if n.type == type_filter]
        if primitive_filter:
            result = [n for n in result if primitive_filter in n.primitives]
        return result

    @property
    def global_content(self) -> Optional[str]:
        return self._global_content

    # ------------------------------------------------------------------ #
    # Planner tool schema (used by GoBIQ chat)
    # ------------------------------------------------------------------ #

    def get_planner_tool_schema(self) -> dict:
        """Build the knowledge_retrieval_tool definition for the chat planner."""
        return {
            "name": "knowledge_retrieval_tool",
            "description": self._build_tool_description(),
            "input_schema": {
                "type": "object",
                "properties": {
                    "node_id": {
                        "type": "string",
                        "enum": self._get_planner_enum(),
                        "description": (
                            "Select the knowledge node. Domain nodes include overview "
                            "content. Topic nodes include specific detail + parent context."
                        ),
                    }
                },
                "required": ["node_id"],
            },
        }

    def _get_planner_enum(self) -> List[str]:
        return sorted(n.id for n in self._nodes.values() if n.expose_to_planner)

    def _build_tool_description(self) -> str:
        lines = [
            "Retrieve analysis knowledge for a specific domain or topic. "
            "Call this FIRST before writing queries. "
            "Available domains and their topics:"
        ]

        domains = [
            n for n in self._nodes.values()
            if n.type == "domain" and n.expose_to_planner
        ]
        templates = [
            n for n in self._nodes.values()
            if n.type == "template" and n.expose_to_planner
        ]

        for domain in sorted(domains, key=lambda n: n.id):
            topic_descs = []
            for child_id in domain.children:
                child = self._nodes.get(child_id)
                if child and child.expose_to_planner:
                    topic_descs.append(f"{child.id} ({child.description})")
            line = f"\n{domain.id} — {domain.description}"
            if topic_descs:
                line += f" Topics: {', '.join(topic_descs)}"
            lines.append(line)

        if templates:
            template_descs = [
                f"{t.id} ({t.description})"
                for t in sorted(templates, key=lambda n: n.id)
            ]
            lines.append(f"\nTemplates: {', '.join(template_descs)}")

        return " ".join(lines)

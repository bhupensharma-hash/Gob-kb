"""
Schema constants and validators for the knowledge graph.

The single source of truth for the schema lives in knowledge/_schema.yaml.
This module loads it once and exposes Python-side constants + validation helpers
used by the loader and by tests/.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import yaml


_SCHEMA_PATH = Path(__file__).resolve().parent.parent.parent / "knowledge" / "_schema.yaml"


def load_schema() -> Dict[str, Any]:
    """Load knowledge/_schema.yaml as a dict."""
    with open(_SCHEMA_PATH, "r") as f:
        return yaml.safe_load(f)


_SCHEMA = load_schema()

VALID_NODE_TYPES = set(_SCHEMA.get("node_types", []))
VALID_RELATION_TYPES = set(_SCHEMA.get("relation_types", []))
VALID_TRAVERSAL_STEP_TYPES = set(_SCHEMA.get("traversal_step_types", []))
VALID_PRIMITIVES = set(_SCHEMA.get("primitives", []))
REQUIRED_FIELDS = set(_SCHEMA.get("required_fields", []))


def validate_node_dict(node_id: str, data: Dict[str, Any]) -> List[str]:
    """
    Validate a single _node.yaml dict against the schema.

    Returns a list of error messages (empty = valid).
    """
    errors: List[str] = []

    # Required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"{node_id}: missing required field '{field}'")

    # Type
    node_type = data.get("type")
    if node_type and node_type not in VALID_NODE_TYPES:
        errors.append(
            f"{node_id}: invalid type '{node_type}' "
            f"(must be one of: {sorted(VALID_NODE_TYPES)})"
        )

    # ID matches expected pattern (dot-separated lowercase)
    if "id" in data and not all(c.isalnum() or c in "._-" for c in data["id"]):
        errors.append(f"{node_id}: id contains invalid characters")

    # Description length
    description = data.get("description", "")
    if len(description) > 200:
        errors.append(
            f"{node_id}: description is {len(description)} chars (recommended <100)"
        )

    # Primitives
    for prim in data.get("primitives", []):
        if prim not in VALID_PRIMITIVES:
            errors.append(
                f"{node_id}: invalid primitive '{prim}' "
                f"(must be one of: {sorted(VALID_PRIMITIVES)})"
            )

    # Relations
    for rel in data.get("related", []):
        rel_type = rel.get("relation")
        if rel_type and rel_type not in VALID_RELATION_TYPES:
            errors.append(
                f"{node_id}: invalid relation type '{rel_type}' "
                f"(must be one of: {sorted(VALID_RELATION_TYPES)})"
            )

    # Playbook traversal validation
    if node_type == "playbook":
        traversal = data.get("traversal", [])
        if not traversal:
            errors.append(f"{node_id}: playbook node must have non-empty 'traversal'")
        for i, step in enumerate(traversal):
            step_type = step.get("step")
            if step_type not in VALID_TRAVERSAL_STEP_TYPES:
                errors.append(
                    f"{node_id}: traversal[{i}] has invalid step type '{step_type}'"
                )

    # metric_relationship validation
    if node_type == "metric_relationship":
        for required in ("source_metric", "target_metric", "direction", "mechanism_short"):
            if not data.get(required):
                errors.append(
                    f"{node_id}: metric_relationship must declare '{required}'"
                )
        valid_directions = {
            "increase_causes_increase",
            "decrease_causes_increase",
            "decrease_causes_decrease",
            "increase_causes_decrease",
        }
        direction = data.get("direction")
        if direction and direction not in valid_directions:
            errors.append(
                f"{node_id}: invalid direction '{direction}' "
                f"(must be one of: {sorted(valid_directions)})"
            )
        valid_confidences = {"high", "medium", "low"}
        confidence = data.get("confidence")
        if confidence and confidence not in valid_confidences:
            errors.append(
                f"{node_id}: invalid confidence '{confidence}' "
                f"(must be one of: {sorted(valid_confidences)})"
            )

    return errors


__all__ = [
    "load_schema",
    "validate_node_dict",
    "VALID_NODE_TYPES",
    "VALID_RELATION_TYPES",
    "VALID_TRAVERSAL_STEP_TYPES",
    "VALID_PRIMITIVES",
    "REQUIRED_FIELDS",
]

"""
Schema validation — every _node.yaml in knowledge/ must conform to _schema.yaml.

Runs in CI on every PR. PRs cannot merge if any test fails.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from gobiq_knowledge.schema import validate_node_dict


KNOWLEDGE_ROOT = Path(__file__).resolve().parent.parent / "knowledge"


def _all_node_files():
    return sorted(KNOWLEDGE_ROOT.rglob("_node.yaml"))


@pytest.mark.parametrize("node_file", _all_node_files(), ids=lambda p: str(p.relative_to(KNOWLEDGE_ROOT)))
def test_node_validates(node_file: Path):
    """Every _node.yaml file must validate against the schema."""
    with open(node_file, "r") as f:
        data = yaml.safe_load(f)

    assert data is not None, f"{node_file} is empty or unparseable"
    assert "id" in data, f"{node_file} missing 'id'"

    errors = validate_node_dict(data["id"], data)
    assert not errors, f"Schema errors in {node_file}:\n  - " + "\n  - ".join(errors)


def test_node_id_matches_folder_path():
    """Every node's id must match its folder path (dot-separated)."""
    failures = []
    for node_file in _all_node_files():
        with open(node_file, "r") as f:
            data = yaml.safe_load(f)
        if not data or "id" not in data:
            continue

        # Folder path relative to knowledge/ root, dot-separated
        rel = node_file.parent.relative_to(KNOWLEDGE_ROOT)
        expected_id = ".".join(rel.parts)

        if data["id"] != expected_id:
            failures.append(
                f"{node_file}: id='{data['id']}' but folder suggests '{expected_id}'"
            )

    assert not failures, "Node ID/folder mismatches:\n  - " + "\n  - ".join(failures)

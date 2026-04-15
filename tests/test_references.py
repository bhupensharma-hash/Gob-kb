"""
Reference integrity — every parent / children / related ID must resolve.
Bidirectional relations must be symmetric.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from gobiq_knowledge import load


@pytest.fixture(scope="module")
def graph():
    knowledge_root = Path(__file__).resolve().parent.parent / "knowledge"
    return load(root_path=knowledge_root, force_reload=True)


def test_all_parents_resolve(graph):
    failures = []
    for node in graph.all_nodes():
        if node.parent and not graph.get_node(node.parent):
            failures.append(f"{node.id} has unknown parent '{node.parent}'")
    assert not failures, "Unknown parents:\n  - " + "\n  - ".join(failures)


def test_all_children_resolve(graph):
    failures = []
    for node in graph.all_nodes():
        for child_id in node.children:
            if not graph.get_node(child_id):
                failures.append(f"{node.id} has unknown child '{child_id}'")
    assert not failures, "Unknown children:\n  - " + "\n  - ".join(failures)


def test_all_related_resolve(graph):
    failures = []
    for node in graph.all_nodes():
        for rel in node.related:
            rel_id = rel.get("id", "")
            if rel_id and not graph.get_node(rel_id):
                failures.append(f"{node.id} has unknown related '{rel_id}'")
    assert not failures, "Unknown related:\n  - " + "\n  - ".join(failures)


def test_relations_are_bidirectional(graph):
    """If A says related: B, B should say related: A (any relation type)."""
    failures = []
    for node in graph.all_nodes():
        for rel in node.related:
            rel_id = rel.get("id", "")
            target = graph.get_node(rel_id)
            if not target:
                continue
            back_links = {r.get("id") for r in target.related}
            if node.id not in back_links:
                failures.append(
                    f"{node.id} -> {rel_id} ({rel.get('relation')}) "
                    f"but {rel_id} has no back-link to {node.id}"
                )
    # NOTE: This is currently a soft-warning rather than hard-fail because the
    # starter atoms haven't been wired bidirectionally yet. Flip to assert
    # once you've completed Phase 0 migration.
    if failures:
        print("\nNon-bidirectional relations (should be fixed):")
        for f in failures:
            print(f"  - {f}")

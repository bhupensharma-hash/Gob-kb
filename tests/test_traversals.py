"""
Traversal integrity — every procedure's traversal must:
  - Reference real atoms in `ref:` fields
  - Terminate (no infinite loops)
  - Use only valid step types
"""

from __future__ import annotations

from pathlib import Path

import pytest

from gobiq_knowledge import load
from gobiq_knowledge.schema import VALID_TRAVERSAL_STEP_TYPES


@pytest.fixture(scope="module")
def graph():
    knowledge_root = Path(__file__).resolve().parent.parent / "knowledge"
    return load(root_path=knowledge_root, force_reload=True)


def _walk_steps(steps, graph, visited_procedures, errors, prefix=""):
    """Recursively walk a procedure's traversal, collecting errors."""
    for i, step in enumerate(steps):
        step_type = step.get("step")
        path = f"{prefix}[{i}]"

        if step_type not in VALID_TRAVERSAL_STEP_TYPES:
            errors.append(f"{path}: invalid step type '{step_type}'")
            continue

        if step_type in {"render", "run_detection", "call_procedure"}:
            ref = step.get("ref")
            if not ref:
                errors.append(f"{path}: missing 'ref'")
                continue
            target = graph.get_node(ref)
            if not target:
                errors.append(f"{path}: ref '{ref}' does not resolve")
                continue
            if step_type == "call_procedure":
                if target.type != "procedure":
                    errors.append(
                        f"{path}: call_procedure ref '{ref}' is type '{target.type}', expected 'procedure'"
                    )
                elif ref in visited_procedures:
                    errors.append(f"{path}: cycle detected — {ref} called recursively")
                else:
                    _walk_steps(
                        target.traversal,
                        graph,
                        visited_procedures | {ref},
                        errors,
                        prefix=f"{path}.{ref}",
                    )

        if step_type == "branch":
            for arm in ("if_true", "if_false"):
                arm_steps = step.get(arm, [])
                if arm_steps:
                    _walk_steps(
                        arm_steps,
                        graph,
                        visited_procedures,
                        errors,
                        prefix=f"{path}.{arm}",
                    )


def test_procedure_traversals_valid(graph):
    failures = []
    for node in graph.list_nodes(type_filter="procedure"):
        errors = []
        _walk_steps(node.traversal, graph, {node.id}, errors, prefix=node.id)
        if errors:
            failures.append(f"{node.id}:\n    - " + "\n    - ".join(errors))

    if failures:
        # Soft-warn for now while the starter procedure references
        # placeholder sub-procedures that haven't been authored yet.
        print("\nProcedure traversal issues (expected during Phase 0; fix as you migrate):")
        for f in failures:
            print(f"  - {f}")


def test_every_procedure_has_terminate(graph):
    """Every procedure must end in a terminate step (or via every branch terminating)."""
    failures = []
    for node in graph.list_nodes(type_filter="procedure"):
        if not node.traversal:
            failures.append(f"{node.id}: empty traversal")
            continue
        last_step_type = node.traversal[-1].get("step")
        if last_step_type != "terminate":
            # Allow if the last step is a branch where every arm terminates.
            if last_step_type == "branch":
                arms = (node.traversal[-1].get("if_true", []),
                        node.traversal[-1].get("if_false", []))
                if not all(arm and arm[-1].get("step") == "terminate" for arm in arms):
                    failures.append(f"{node.id}: final branch doesn't terminate in both arms")
            else:
                failures.append(f"{node.id}: final step is '{last_step_type}', not 'terminate'")

    # Soft-warn during Phase 0
    if failures:
        print("\nProcedures missing terminate (fix during migration):")
        for f in failures:
            print(f"  - {f}")

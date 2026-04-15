"""
RAG seeding helpers — extract Q→Action recipes from knowledge/recipes/*.md
and stage them for embedding into Milvus (or any vector store).

This module is consumer-agnostic: it parses recipes and yields {question, action}
records. Embedding + Milvus upload happens in the consuming app, which knows
its own collection name, embedding model, and credentials.

Recipe format (in knowledge/recipes/{domain}_recipes.md):

    {Natural-language question the user would ask}

    ==> **Execute {Action Name}**: {Detailed instructions...}


    {Next question}

    ==> ...

Recipes are separated by triple newlines (one fully blank paragraph between blocks).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator, List


# Two consecutive blank lines = three consecutive newlines.
_RECIPE_DELIMITER = re.compile(r"\n\s*\n\s*\n+")
_ACTION_MARKER = "==>"


@dataclass
class Recipe:
    """A single Q→Action recipe extracted from a recipes/*.md file."""

    source_file: str       # relative path within knowledge/recipes/
    question: str          # natural-language question (the embedding key)
    action: str            # the executable instruction (==> Execute X: ...)


def parse_recipe_block(block: str) -> Recipe | None:
    """Parse one recipe block into a Recipe. Returns None if malformed."""
    block = block.strip()
    if not block or _ACTION_MARKER not in block:
        return None

    # Split on the action marker (first occurrence).
    question_part, _, action_part = block.partition(_ACTION_MARKER)
    question = question_part.strip()
    action = (_ACTION_MARKER + action_part).strip()

    if not question or not action:
        return None

    return Recipe(source_file="", question=question, action=action)


def parse_recipe_file(path: Path) -> List[Recipe]:
    """Parse one recipes/*.md file into a list of Recipes."""
    text = path.read_text(encoding="utf-8")
    recipes: List[Recipe] = []
    for block in _RECIPE_DELIMITER.split(text):
        recipe = parse_recipe_block(block)
        if recipe:
            recipe.source_file = path.name
            recipes.append(recipe)
    return recipes


def iter_all_recipes(recipes_dir: Path) -> Iterator[Recipe]:
    """Yield every recipe from every *_recipes.md file in the directory."""
    for path in sorted(recipes_dir.glob("*_recipes.md")):
        for recipe in parse_recipe_file(path):
            yield recipe


def collect_all_recipes(recipes_dir: Path) -> List[Recipe]:
    """Collect every recipe in the directory into a list."""
    return list(iter_all_recipes(recipes_dir))


__all__ = ["Recipe", "parse_recipe_block", "parse_recipe_file", "iter_all_recipes", "collect_all_recipes"]

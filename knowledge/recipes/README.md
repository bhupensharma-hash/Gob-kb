# recipes/

RAG-indexed Q→Action pairs. Each `*_recipes.md` file holds many recipes,
separated by triple newlines.

## Format

```text
{Natural-language question the user would ask}

==> **Execute {Action Name}**: {Detailed instructions for query_generator_tool
or whatever tool the action invokes — what columns to show, how to filter,
how to sort, how to interpret results, who owns the action.}


{Next question}

==> ...
```

Triple-newline = one blank paragraph between blocks. The `_RECIPE_DELIMITER`
in `src/gobiq_knowledge/rag.py` enforces this.

## Files (after migration)

- `availability_recipes.md`
- `supply_chain_recipes.md`
- `visibility_recipes.md`
- `pricing_recipes.md`
- `market_share_recipes.md`
- `growth_diagnosis_recipes.md`

Migrate from GoBIQ's `backend/app/ai/knowledge/recipes/` during Phase 0.

## Seeding

Consuming apps call `gobiq_knowledge.rag.collect_all_recipes(recipes_dir)` to
get a list of `Recipe` objects, then embed and upload to their own Milvus
collection. The package does not own the vector store.

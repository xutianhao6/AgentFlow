"""Import a workflow template: dependency check + ID remap + private copy."""
from __future__ import annotations

import copy

from agentflow.core.exceptions import DependencyError
from agentflow.utils.ids import gen_id


class WorkflowImporter:
    def check_dependencies(self, dependencies: dict, installed_plugin_ids: set[str]) -> list[str]:
        """Return a list of missing plugin ids (empty == all satisfied)."""
        required = set(dependencies.get("plugins", []) or [])
        missing = [p for p in required if p not in installed_plugin_ids]
        return missing

    def remap_ids(self, dsl: dict) -> dict:
        """Create fresh node ids to avoid collisions, rewriting edges + references."""
        dsl = copy.deepcopy(dsl)
        graph = dsl.get("graph", {})
        id_map: dict[str, str] = {}
        for n in graph.get("nodes", []):
            old = n["id"]
            # keep type prefix for readability
            new = f"{n['type']}_{gen_id()[:6]}"
            id_map[old] = new

        # rewrite node ids
        for n in graph.get("nodes", []):
            n["id"] = id_map[n["id"]]
            # rewrite {{old.field}} references in inputs/prompt/etc
            _rewrite_refs(n.get("data", {}), id_map)

        # rewrite edges
        for e in graph.get("edges", []):
            e["source"] = id_map.get(e["source"], e["source"])
            e["target"] = id_map.get(e["target"], e["target"])

        dsl.pop("workflow_id", None)
        return dsl


def _rewrite_refs(data: dict, id_map: dict) -> None:
    import json
    import re

    raw = json.dumps(data, ensure_ascii=False)
    for old, new in id_map.items():
        raw = re.sub(r"\{\{\s*" + re.escape(old) + r"\.", "{{" + new + ".", raw)
    new_data = json.loads(raw)
    data.clear()
    data.update(new_data)


importer = WorkflowImporter()

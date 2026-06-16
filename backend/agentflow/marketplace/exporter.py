"""Export a workflow as a template (DSL + dependency declaration)."""
from __future__ import annotations


class WorkflowExporter:
    def export(self, wf: dict) -> dict:
        """wf is a dict with keys: name, description, dsl."""
        dsl = wf["dsl"]
        return {
            "dsl": dsl,
            "dependencies": {
                "plugins": self._extract_plugins(dsl),
                "datasets": self._extract_datasets(dsl),  # declaration only, no data
            },
            "meta": {"name": wf.get("name", ""), "description": wf.get("description", "")},
        }

    @staticmethod
    def _extract_plugins(dsl: dict) -> list[str]:
        plugins = []
        for n in dsl.get("graph", {}).get("nodes", []):
            if n.get("type") == "tool":
                pid = n.get("data", {}).get("plugin_id")
                if pid:
                    plugins.append(pid)
        return sorted(set(plugins))

    @staticmethod
    def _extract_datasets(dsl: dict) -> list[str]:
        datasets = []
        for n in dsl.get("graph", {}).get("nodes", []):
            if n.get("type") == "knowledge_retrieval":
                datasets.extend(n.get("data", {}).get("dataset_ids", []) or [])
        return sorted(set(datasets))


exporter = WorkflowExporter()

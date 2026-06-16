"""Knowledge retrieval node — RAG over the knowledge base."""
from __future__ import annotations

from agentflow.engine.nodes.base import BaseNode, NodeIOSpec
from agentflow.engine.nodes.registry import register_node
from agentflow.engine.dsl import FieldSchema
from agentflow.knowledge.retriever import retriever


@register_node
class KnowledgeRetrievalNode(BaseNode):
    type = "knowledge_retrieval"
    category = "AI"
    label = "知识检索"
    icon = "book"
    default_io = NodeIOSpec(
        inputs=[FieldSchema(name="query", type="string", required=True)],
        outputs=[FieldSchema(name="result", type="array[object]", description="检索到的文档块")],
    )

    def run(self, inputs: dict, state: dict) -> dict:
        query = inputs.get("query") or ""
        docs = retriever.retrieve(
            query=query,
            dataset_ids=self.data.get("dataset_ids", []),
            top_k=int(self.data.get("top_k", 3)),
            score_threshold=float(self.data.get("score_threshold", 0.5)),
            search_mode=self.data.get("search_mode", "hybrid"),
            rerank=bool(self.data.get("rerank_enabled", False)),
            semantic_weight=float(self.data.get("semantic_weight", 0.7)),
            keyword_weight=float(self.data.get("keyword_weight", 0.3)),
        )
        return {"result": docs}

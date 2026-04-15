"""
Assemblers — the two consumers of the knowledge graph.

- chat: depth-1 walk, returns Layer 0+1 retrieval context for one node + neighbors.
- report: depth-N walk, executes a procedure end-to-end and renders to HTML.

Both assemblers consume the SAME KnowledgeGraph. They differ only in how
much of the graph they walk per call.
"""

from .chat import assemble_chat_context
from .report import assemble_report

__all__ = ["assemble_chat_context", "assemble_report"]

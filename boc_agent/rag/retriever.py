import os
from typing import List, Dict, Any, Optional
from boc_agent.rag.document_loader import load_documents
from boc_agent.rag.chunker import chunk_documents
from boc_agent.rag.vector_store import RetrievalIndex

# Global in-memory singleton index
_GLOBAL_INDEX: Optional[RetrievalIndex] = None

def get_or_create_index(base_dir: str = ".", force_rebuild: bool = False) -> RetrievalIndex:
    """Fetches the global singleton index, building it lazily if not already created."""
    global _GLOBAL_INDEX
    if _GLOBAL_INDEX is None or force_rebuild:
        index = RetrievalIndex()
        # Ingest documents and build chunks
        docs = load_documents(base_dir)
        chunks = chunk_documents(docs)
        index.build_index(chunks)
        _GLOBAL_INDEX = index
    return _GLOBAL_INDEX

class DocRetriever:
    """Retriever class to fetch relevant documentation passages from the index."""
    def __init__(self, base_dir: str = "."):
        self.base_dir = base_dir

    def retrieve(self, query_text: str, top_k: int = 3, min_score: float = 0.05) -> List[Dict[str, Any]]:
        """Queries the documentation index and returns the top-k chunks."""
        index = get_or_create_index(self.base_dir)
        return index.query(query_text, top_k=top_k, min_score=min_score)

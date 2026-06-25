from typing import List, Dict, Any
from boc_agent.rag.embedding import TfidfVectorizer, compute_cosine_similarity

class RetrievalIndex:
    """In-memory retrieval index mapping document chunks to TF-IDF vectors."""
    def __init__(self):
        self.chunks: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer()
        self.vectors: List[Dict[int, float]] = []

    def build_index(self, chunks: List[Dict[str, Any]]) -> None:
        """Fits vocabulary and computes TF-IDF representations for all chunks."""
        self.chunks = chunks
        excerpts = [c["excerpt"] for c in chunks]
        self.vectorizer.fit(excerpts)
        self.vectors = [self.vectorizer.transform(excerpt) for excerpt in excerpts]

    def query(self, query_text: str, top_k: int = 3, min_score: float = 0.05) -> List[Dict[str, Any]]:
        """Queries the index, computes similarity, and returns top-k matching chunks sorted by score descending."""
        query_vector = self.vectorizer.transform(query_text)
        if not query_vector:
            return []
            
        results = []
        for idx, chunk in enumerate(self.chunks):
            chunk_vector = self.vectors[idx]
            score = compute_cosine_similarity(query_vector, chunk_vector)
            if score >= min_score:
                results.append({
                    "chunk": chunk,
                    "score": score
                })
                
        # Sort by score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        
        # Return only the chunk details for top-k
        return [r["chunk"] for r in results[:top_k]]

    def to_json_dict(self) -> Dict[str, Any]:
        """Converts the index to a serializable dictionary (optional JSON caching)."""
        return {
            "vocab": self.vectorizer.vocab,
            "idf": self.vectorizer.idf,
            "num_docs": self.vectorizer.num_docs,
            "chunks": self.chunks,
            # JSON keys must be strings
            "vectors": [{str(k): v for k, v in vec.items()} for vec in self.vectors]
        }

    def from_json_dict(self, data: Dict[str, Any]) -> None:
        """Loads index state from a serializable dictionary."""
        self.vectorizer.vocab = data["vocab"]
        self.vectorizer.idf = data["idf"]
        self.vectorizer.num_docs = data["num_docs"]
        self.chunks = data["chunks"]
        self.vectors = [{int(k): v for k, v in vec.items()} for vec in data["vectors"]]

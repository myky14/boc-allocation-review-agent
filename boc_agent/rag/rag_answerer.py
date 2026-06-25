from boc_agent.rag.retriever import DocRetriever

class RAGAnswerer:
    """Answers documentation and policy questions by retrieving matched chunks from repo files."""
    def __init__(self, base_dir: str = "."):
        self.retriever = DocRetriever(base_dir)

    def answer(self, question: str, top_k: int = 3) -> str:
        """Retrieves matching chunks and builds a grounded markdown response."""
        chunks = self.retriever.retrieve(question, top_k=top_k)
        
        if not chunks:
            return "No relevant repository documentation was found for this question. Please rephrase or check the walkthrough."
            
        intro = "### 📚 Documentation Reference\n\nBased on the repository documentation, here are the most relevant sections:\n\n"
        
        excerpts_list = []
        for idx, chunk in enumerate(chunks, 1):
            src = chunk.get("source_file", "N/A")
            header = chunk.get("header", "N/A")
            excerpt_text = chunk.get("excerpt", "").strip()
            
            excerpts_list.append(
                f"> **[Reference {idx}]**\n"
                f"> *Source file: [{src}]({src}) (Section: {header})*\n"
                f">\n"
                f"> {excerpt_text}"
            )
            
        body = "\n\n".join(excerpts_list)
        
        disclaimer = (
            "\n\n---\n"
            "⚠️ **Disclaimer**: This response is grounded in repository documentation and does "
            "not provide official tax, legal, CRA, CAVCO, Ontario Creates, or SODEC determinations."
        )
        
        return intro + body + disclaimer

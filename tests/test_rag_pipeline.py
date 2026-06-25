import os
import sys
import pytest
import pandas as pd
from boc_agent.rag.document_loader import load_documents
from boc_agent.rag.chunker import chunk_documents
from boc_agent.rag.embedding import TfidfVectorizer, tokenize
from boc_agent.rag.vector_store import RetrievalIndex
from boc_agent.rag.retriever import DocRetriever, get_or_create_index
from boc_agent.rag.rag_answerer import RAGAnswerer
from boc_agent.chat.query_router import route_query
from boc_agent.chat.assistant import ReviewConversationAssistant

def test_document_loader_loads_and_skips_missing(tmp_path):
    base_dir = str(tmp_path)
    readme_content = "This is a README mock content."
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    arch_content = "# Architecture\nSome architecture content."
    prob_content = "# Problem\nSome problem content."
    
    with open(os.path.join(base_dir, "README.md"), "w", encoding="utf-8") as f:
        f.write(readme_content)
    with open(os.path.join(base_dir, "docs", "architecture.md"), "w", encoding="utf-8") as f:
        f.write(arch_content)
    with open(os.path.join(base_dir, "docs", "problem_statement.md"), "w", encoding="utf-8") as f:
        f.write(prob_content)
    with open(os.path.join(base_dir, "docs", "binary_file.bin"), "wb") as f:
        f.write(b"\x00\x01\x02")
    with open(os.path.join(base_dir, "docs", "output.txt"), "w", encoding="utf-8") as f:
        f.write("text content")
        
    docs = load_documents(base_dir)
    assert len(docs) == 3
    sources = [d["source_file"] for d in docs]
    assert "README.md" in sources
    assert "docs/architecture.md" in sources
    assert "docs/problem_statement.md" in sources
    assert "docs/binary_file.bin" not in sources
    assert "docs/output.txt" not in sources

def test_document_loader_loads_all_real_docs():
    docs = load_documents(".")
    sources = [d["source_file"] for d in docs]
    expected_files = [
        "README.md",
        "PROJECT_CONTEXT.md",
        "walkthrough.md",
        "docs/architecture.md",
        "docs/demo_cases.md",
        "docs/evaluation_plan.md",
        "docs/mvp_scope.md",
        "docs/problem_statement.md",
    ]
    for ef in expected_files:
        assert ef in sources, f"Expected {ef} to be loaded by document_loader, but it was not."


def test_chunker_metadata_and_non_empty(tmp_path):
    base_dir = str(tmp_path)
    arch_content = (
        "# System Architecture\n"
        "This is paragraph one.\n"
        "## Sub Heading\n"
        "This is paragraph two."
    )
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    with open(os.path.join(base_dir, "docs", "architecture.md"), "w", encoding="utf-8") as f:
        f.write(arch_content)
        
    docs = load_documents(base_dir)
    chunks = chunk_documents(docs, chunk_size=100, overlap=10)
    
    assert len(chunks) > 0
    for chunk in chunks:
        assert chunk["source_file"] == "docs/architecture.md"
        assert chunk["header"] in ["System Architecture", "Sub Heading"]
        assert len(chunk["excerpt"].strip()) > 0


def test_tfidf_vectorizer_ranking():
    chunks = [
        {"excerpt": "Location 920 represents costs incurred outside of Canada and is treated as ineligible provincial spend.", "header": "Location", "source_file": "docs/architecture.md"},
        {"excerpt": "The orchestrator executes the tools in a structured, sequential workflow pipeline.", "header": "Orchestration", "source_file": "docs/architecture.md"},
        {"excerpt": "Greenslate, Cast & Crew are payroll processors.", "header": "Payees", "source_file": "docs/architecture.md"}
    ]
    
    index = RetrievalIndex()
    index.build_index(chunks)
    
    results = index.query("Explain what Location 920 represents", top_k=1)
    assert len(results) == 1
    assert "Location 920 represents costs" in results[0]["excerpt"]


def test_retriever_returns_top_k():
    chunks = [
        {"excerpt": "First match has location 920 details.", "header": "H1", "source_file": "doc1.md"},
        {"excerpt": "Second match has location 920 metadata.", "header": "H2", "source_file": "doc1.md"},
        {"excerpt": "Third match has location 920 details.", "header": "H3", "source_file": "doc1.md"},
        {"excerpt": "Fourth match is unrelated spend data.", "header": "H4", "source_file": "doc1.md"}
    ]
    index = RetrievalIndex()
    index.build_index(chunks)
    
    res = index.query("location 920", top_k=2)
    assert len(res) == 2


def test_rag_answer_formatting():
    answerer = RAGAnswerer()
    res = answerer.answer("What is Location 920?")
    assert "### 📚 Documentation Reference" in res
    assert "Source file:" in res
    assert "Disclaimer" in res
    assert "does not provide official tax, legal, CRA, CAVCO" in res
    
    # Assert that file:/// is not in the output
    assert "file:///" not in res
    
    # Assert that relative markdown links are present for source files
    import re
    match = re.search(r"Source file:\s*\[([^\]]+)\]\(([^)]+)\)", res)
    assert match is not None, "Could not find formatted source file markdown link."
    label, link = match.groups()
    assert label == link, f"Label '{label}' and link '{link}' should be identical relative paths"
    assert not label.startswith("/"), "Should not be absolute path"
    assert "file:" not in link, "Should not contain file: protocol"


def test_rag_unrelated_query_fallback():
    answerer = RAGAnswerer()
    res = answerer.answer("What is the capital of France?")
    assert "No relevant repository documentation was found" in res


def test_query_router_routes_doc_to_rag():
    assert route_query("What is Location 920?") == "rag"
    assert route_query("Explain the HITL workflow.") == "rag"
    assert route_query("Where is prompt injection handled?") == "rag"
    assert route_query("What is the architecture?") == "rag"
    assert route_query("What are the project limitations?") == "rag"
    assert route_query("What does Ontario Individual 45 mean?") == "rag"
    assert route_query("Explain the workflow.") == "rag"
    assert route_query("What is the difference between the chat assistant and RAG?") == "rag"


def test_query_router_does_not_route_row_to_rag():
    assert route_query("Why is row 12 Needs Human Review?") == "row_explanation"
    assert route_query("Explain Trans Ref 508841.") == "row_explanation"
    assert route_query("Show Location 920 rows.") == "filter_location"
    assert route_query("Which rows are ineligible?") == "ineligible_summary"
    assert route_query("Summarize the review queue.") == "review_queue_summary"


def test_assistant_answers_docs_without_df():
    assistant = ReviewConversationAssistant()
    res = assistant.answer("What is the architecture?", None)
    assert "### 📚 Documentation Reference" in res
    
    res_empty = assistant.answer("What is the architecture?", pd.DataFrame())
    assert "### 📚 Documentation Reference" in res_empty


def test_assistant_returns_review_first_for_row_without_df():
    assistant = ReviewConversationAssistant()
    res = assistant.answer("explain transaction 508841", None)
    assert "No reviewed workbook data is currently loaded. Transaction not found / run review first." in res
    
    res_empty = assistant.answer("explain row 12", pd.DataFrame())
    assert "No reviewed workbook data is currently loaded. Transaction not found / run review first." in res


def test_assistant_non_mutation_for_rag():
    assistant = ReviewConversationAssistant()
    df = pd.DataFrame([{"trans_ref": "508841", "vendor_name": "Test"}])
    df_orig = df.copy()
    
    assistant.answer("What is Location 920?", df)
    pd.testing.assert_frame_equal(df, df_orig)


def test_no_heavy_dependencies():
    heavy_modules = ["sentence_transformers", "faiss", "chromadb", "langchain", "llama_index"]
    for mod in heavy_modules:
        assert mod not in sys.modules

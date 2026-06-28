import os
import re
import pytest

def test_portfolio_docs_exist():
    assert os.path.exists("docs/portfolio_case_study.md")
    assert os.path.exists("docs/demo_script.md")
    assert os.path.exists("docs/release_checklist.md")
    assert os.path.exists("docs/interview_notes.md")

def test_readme_links_to_portfolio_docs():
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read().lower()
    
    assert "portfolio_case_study.md" in readme
    assert "demo_script.md" in readme
    assert "release_checklist.md" in readme

def test_docs_avoid_false_deployment_claims():
    # Issue 3: Scan all portfolio docs, release checklist, and README using normalized text and broad regex/family patterns
    files_to_check = [
        "docs/portfolio_case_study.md",
        "docs/demo_script.md",
        "docs/release_checklist.md",
        "docs/interview_notes.md",
        "README.md"
    ]
    
    patterns_to_reject = [
        # 1. Native ADK deployment/implementation/activation
        r'\b(?:native\s+)?(?:google\s+)?adk\s+(?:\w+\s+){0,3}(?:deployed|implemented|active|live)\b',
        
        # 2. Vertex AI deployment/integration/activation
        r'\bvertex\s+ai\s+(?:agent\s+engine\s+)?(?:\w+\s+){0,3}(?:deployed|implemented|active|live|integrated)\b',
        r'\bagent\s+engine\s+(?:\w+\s+){0,3}(?:deployed|implemented|active|live)\b',
        
        # 3. Gemini deployment/integration/activation
        r'\bgemini\s+(?:integration\s+)?(?:\w+\s+){0,3}(?:deployed|implemented|active|live|integrated)\b',
        r'\bgemini\s+has\s+been\s+integrated\b',
        
        # 4. Automatic accounting/allocation/eligibility decisions
        r'\bautomat(?:ic|ed)\s+(?:\w+\s+)?accounting\s+decision\b',
        r'\bautomatically\s+(?:decides\s+allocations|makes\s+allocation\s+decisions|determines\s+eligibility)\b',
        
        # 5. Official compliance authority
        r'\bofficial\s+(?:cra|cavco|tax)\s+(?:compliance|engine)\b',
        r'\bofficial\s+compliance\s+engine\b',
        r'\bproduction[- ](?:ready|grade)\s+compliance\s+ai\b',
        
        # 6. Absolute precision/safety
        r'\b100%\s+precise\b',
        r'\bmathematical\s+precision\b',
        r'\bcomplete\s+compliance\s+safety\b'
    ]
    
    # Direct exact-match strings to reject (keeping previous negative checks)
    exact_claims = [
        "production-grade tax engine",
        "official compliance engine",
        "native google adk deployment",
        "vertex ai integration",
        "gemini-powered agent",
        "production-ready accounting ai",
        "production grade accounting ai",
        "official cra compliance",
        "official cavco compliance",
        "official tax compliance engine",
        "native adk deployment",
        "google adk deployment",
        "vertex ai deployed",
        "vertex ai is deployed",
        "gemini integrated",
        "gemini is integrated",
        "automatic accounting decisions",
        "automated accounting decisions",
        "100% precise",
        "mathematical precision",
        "complete compliance safety",
        "official tax guidelines"
    ]
    
    for filepath in files_to_check:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().lower()
            # Collapse whitespace and optionally replace punctuation with spaces
            normalized_content = re.sub(r'[^a-z0-9%\s\-]', ' ', content)
            normalized_content = re.sub(r'\s+', ' ', normalized_content)
        
        # Check exact claims first
        for claim in exact_claims:
            assert claim not in normalized_content, f"Exact false claim '{claim}' found in {filepath}"
            
        # Check regex families
        for pattern in patterns_to_reject:
            for match in re.finditer(pattern, normalized_content):
                # Check if match is preceded by negation or future/optional context within 40 characters
                start = max(0, match.start() - 40)
                context = normalized_content[start:match.end()]
                if not any(neg in context for neg in ["not", "no", "future", "optional", "conceptual"]):
                     assert False, f"False claim pattern '{pattern}' matched as '{match.group(0)}' in context '{context}' in file {filepath}"

def test_validate_documented_test_count():
    # Issue 5: Verify portfolio docs do not contain stale test counts (143/144)
    files_to_check = [
        "docs/portfolio_case_study.md",
        "docs/demo_script.md",
        "docs/release_checklist.md",
        "docs/interview_notes.md",
        "README.md",
        "docs/evaluation_plan.md"
    ]
    
    stale_patterns = ["138 tests", "138 passed", "138 passing", "143 tests", "143 passed", "143 passing", "144 tests", "144 passed", "144 passing", "145 tests", "145 passed", "145 passing", "152 tests", "152 passed", "152 passing", "153 tests", "153 passed", "153 passing", "176 tests", "176 passed", "176 passing"]
    
    for filepath in files_to_check:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().lower()
            normalized_content = re.sub(r'\s+', ' ', content)
            
        for pattern in stale_patterns:
            assert pattern not in normalized_content, f"Stale test count pattern '{pattern}' found in {filepath}"
            
    # Verify the current count "183" exists in relevant docs where test count is mentioned
    docs_mentioning_count = [
        "README.md",
        "docs/evaluation_plan.md",
        "docs/portfolio_case_study.md",
        "docs/demo_script.md",
        "docs/release_checklist.md"
    ]
    for filepath in docs_mentioning_count:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().lower()
            normalized_content = re.sub(r'\s+', ' ', content)
        assert ("183 tests" in normalized_content or
                "183 unit tests" in normalized_content or
                "183 unit and integration tests" in normalized_content or
                "183 passed" in normalized_content or
                "183-test" in normalized_content), f"Current test count 183 not mentioned in {filepath}"

def test_safe_disclaimers_per_document():
    # Issue 6: Each main portfolio document must have at least one appropriate disclaimer
    files_to_check = [
        "docs/portfolio_case_study.md",
        "docs/demo_script.md",
        "docs/release_checklist.md",
        "docs/interview_notes.md"
    ]
    
    boundary_phrases = [
        "review support",
        "not official tax",
        "not legal",
        "does not provide official",
        "adk-inspired",
        "not native google adk",
        "no vertex",
        "no gemini",
        "not deployed",
        "synthetic workbook"
    ]
    
    for filepath in files_to_check:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().lower()
            normalized_content = re.sub(r'\s+', ' ', content)
            
        found_any = False
        for phrase in boundary_phrases:
            if phrase in normalized_content:
                found_any = True
                break
        assert found_any, f"No safe disclaimers/boundary phrases found in {filepath}"

def test_release_checklist_contains_allocation_tool_protection():
    with open("docs/release_checklist.md", "r", encoding="utf-8") as f:
        content = f.read().lower()
    
    assert "allocation_tool.py" in content
    assert "git diff" in content
    assert "v2.0.0-portfolio" in content

def test_demo_script_contains_key_sections():
    with open("docs/demo_script.md", "r", encoding="utf-8") as f:
        content = f.read().lower()
    
    assert "opening" in content
    assert "architecture" in content
    assert "cli" in content
    assert "streamlit" in content
    assert "hitl" in content or "human-in-the-loop" in content
    assert "conversational" in content or "assistant" in content
    assert "rag" in content or "retriever" in content
    assert "trace" in content or "observability" in content
    assert "docker" in content or "cloud run" in content

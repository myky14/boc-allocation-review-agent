import os
import pytest

def test_adk_migration_guide_exists_and_valid():
    guide_path = "docs/adk_vertex_migration.md"
    assert os.path.exists(guide_path), "adk_vertex_migration.md must exist in docs/"
    
    with open(guide_path, "r", encoding="utf-8") as f:
        content = f.read()
        lower_content = content.lower()
    
    # 1. Structural checklist, mapping and reference assertions
    assert "adk mapping" in lower_content
    assert "vertex ai mapping" in lower_content or "vertex mapping" in lower_content
    assert "migration checklist" in lower_content
    
    # 2. Positive checks: Require guide to contain roadmapping keywords (Issue 3)
    assert "optional" in lower_content
    assert "conceptual" in lower_content
    assert "future" in lower_content
    assert "not implemented" in lower_content
    assert "not currently deployed" in lower_content or "no native cloud agent deployment exists" in lower_content
    assert "allocation_tool.py" in lower_content
    assert "source of truth" in lower_content
    
    # 3. Positive checks: Require the migration guide to independently state these disclaimers (Issue 3)
    assert "google adk is not implemented" in lower_content
    assert "vertex ai agent engine is not deployed" in lower_content
    assert "gemini is not integrated" in lower_content
    assert "vertex ai search is not active" in lower_content
    assert "migration remains" in lower_content or "future migration" in lower_content
    
    # 4. Negative assertions for broad false claims (Issue 3)
    negative_claims = [
        "native adk is active",
        "google adk is active",
        "adk is implemented",
        "vertex ai is deployed",
        "agent engine has been deployed",
        "agent engine is active",
        "gemini is integrated",
        "vertex ai search is active",
        "native google adk deployment exists",
        
        # New variants to reject (Issue 3)
        "vertex ai agent engine is deployed",
        "vertex ai agent engine has been deployed",
        "vertex ai agent engine is active",
        "gemini integration is active",
        "gemini integration has been implemented",
        "gemini has been integrated",
        "vertex ai search has been activated",
        "vertex ai search has been deployed",
        "vertex ai search is deployed",
        "google adk has been implemented",
        "native google adk is active",
        "native google adk has been deployed"
    ]
    
    for claim in negative_claims:
        assert claim not in lower_content, f"False claim detected: '{claim}'"
        
    # 5. Core logic preservation statements
    assert "must remain unchanged" in lower_content or "must remain completely unchanged" in lower_content
    assert "replace orchestration" in lower_content or "replace orchestration and runtime" in lower_content

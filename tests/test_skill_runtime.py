import os
import pytest
import pandas as pd
from boc_agent.skill.loader import SkillLoader, get_active_skill
from boc_agent.skill.models import Skill
from boc_agent.chat.query_router import route_query
from boc_agent.chat.assistant import ReviewConversationAssistant

@pytest.fixture
def temp_skill_config(tmp_path):
    """Configures environment to point to a temporary skill file, clearing on teardown."""
    orig_env = os.environ.get("BOC_SKILL_FILE_PATH")
    
    def _write_config(content: str):
        file_path = tmp_path / "SKILL_temp.md"
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        os.environ["BOC_SKILL_FILE_PATH"] = str(file_path)
        # Force reload active skill cache
        SkillLoader().load_from_file(force_reload=True)
        return str(file_path)

    yield _write_config

    # Cleanup
    if orig_env is not None:
        os.environ["BOC_SKILL_FILE_PATH"] = orig_env
    else:
        os.environ.pop("BOC_SKILL_FILE_PATH", None)
    # Reload root SKILL.md
    SkillLoader().load_from_file(force_reload=True)


def test_valid_skill_loading():
    """Verifies that the active repository SKILL.md loads and parses successfully."""
    # Ensure active skill loads root SKILL.md
    loader = SkillLoader()
    skill = loader.load_from_file("SKILL.md", force_reload=True)
    assert isinstance(skill, Skill)
    assert skill.metadata.name == "boc_allocation_review_assistant"
    assert "dataframe_lookup" in skill.capabilities
    assert "documentation_rag" in skill.capabilities
    
    # Check that tools are parsed and mapped
    tool_names = {t.name for t in skill.tools}
    assert "classification_tool" in tool_names
    assert "RAG_retriever" in tool_names


def test_valid_skill_loading_from_temp(temp_skill_config):
    """Verifies valid skill configuration loads correctly from a temp file."""
    valid_content = """---
name: valid_temp_skill
version: 2.1.0
description: Valid mock skill
role: Tester
capabilities:
  - dataframe_lookup: "Explanation"
  - documentation_rag: "Documentation"
non_capabilities:
  - tax_determinations: "No tax credit determinations"
---
# Configuration

## Objectives
- Act as test validator.

## Available Tools
- Name: classification_tool
  Intents: ["row_explanation"]
  Mutating: false
  RequiredDataframe: true

## Routing Policies
- Match "test" -> intent: test

## Refusal Policies
- Matches: ["refuse me"]
  RefusalResponse: "Disclaimer refusal"

## Grounding & Citation Policies
- StrictGrounding: true
  OmitProtocols: ["file:///"]
  PathStyle: relative
  RequiredDisclaimer: "Grounding disclaimer"
"""
    temp_skill_config(valid_content)
    skill = get_active_skill()
    assert skill.metadata.name == "valid_temp_skill"
    assert skill.metadata.version == "2.1.0"
    assert "dataframe_lookup" in skill.capabilities
    assert "classification_tool" in {t.name for t in skill.tools}


def test_missing_sections(temp_skill_config):
    """Verifies that loading a SKILL.md missing a required section raises ValueError."""
    bad_skill_content = """---
name: bad_skill
version: 1.0.0
description: bad
role: bad
---
# Configuration

## Objectives
- Do something.
"""
    with pytest.raises(ValueError, match="Missing required section in SKILL.md"):
        temp_skill_config(bad_skill_content)


def test_invalid_tools(temp_skill_config):
    """Verifies that an invalid tool name in SKILL.md raises ValueError."""
    bad_skill_content = """---
name: bad_skill
version: 1.0.0
description: bad
role: bad
---
# Configuration

## Objectives
- Do something.

## Available Tools
- Name: unregistered_hack_tool
  Intents: ["row_explanation"]
  Mutating: false
  RequiredDataframe: true

## Routing Policies
- Match "test" -> intent: test

## Refusal Policies
- Matches: ["refuse me"]
  RefusalResponse: "No"

## Grounding & Citation Policies
- StrictGrounding: true
  OmitProtocols: []
  RequiredDisclaimer: "No"
"""
    with pytest.raises(ValueError, match="Invalid tool Name 'unregistered_hack_tool'"):
        temp_skill_config(bad_skill_content)


def test_mutating_tools_blocked(temp_skill_config):
    """Verifies that defining a tool with mutating=True in SKILL.md raises ValueError."""
    bad_skill_content = """---
name: bad_skill
version: 1.0.0
description: bad
role: bad
---
# Configuration

## Objectives
- Do something.

## Available Tools
- Name: classification_tool
  Intents: ["row_explanation"]
  Mutating: true
  RequiredDataframe: true

## Routing Policies
- Match "test" -> intent: test

## Refusal Policies
- Matches: ["refuse me"]
  RefusalResponse: "No"

## Grounding & Citation Policies
- StrictGrounding: true
  OmitProtocols: []
  RequiredDisclaimer: "No"
"""
    with pytest.raises(ValueError, match="cannot have mutating=True"):
        temp_skill_config(bad_skill_content)


def test_refusal_policy_routing_and_response(temp_skill_config):
    """Verifies that the refusal policy intercepts matches and returns the custom response."""
    content = """---
name: refusal_skill
version: 1.0.0
description: test
role: test
---
# Configuration

## Objectives
- Test refusal.

## Available Tools
- Name: classification_tool
  Intents: ["row_explanation"]

## Routing Policies
- Match "test" -> intent: test

## Refusal Policies
- Matches: ["guarantee my tax credit", "refuse me"]
  RefusalResponse: "Custom Refusal Msg"

## Grounding & Citation Policies
- StrictGrounding: true
  OmitProtocols: []
  RequiredDisclaimer: "No"
"""
    temp_skill_config(content)
    
    question = "guarantee my tax credit"
    intent = route_query(question)
    assert intent == "tax_ruling"
    
    assistant = ReviewConversationAssistant()
    res = assistant.answer(question, None)
    assert "Custom Refusal Msg" in res


def test_grounding_policy_enforcement(temp_skill_config):
    """Verifies that the disclaimer and omitted protocols configured in SKILL.md are respected."""
    content = """---
name: grounding_skill
version: 1.0.0
description: test
role: test
capabilities:
  - documentation_rag
---
# Configuration

## Objectives
- Test grounding.

## Available Tools
- Name: RAG_retriever
  Intents: ["rag"]
  RequiredGrounding: true
  RequiredDataframe: false

## Routing Policies
- Match "What is Location 920" -> intent: rag

## Refusal Policies
- Matches: ["refuse"]
  RefusalResponse: "No"

## Grounding & Citation Policies
- StrictGrounding: true
  OmitProtocols: ["file:///"]
  PathStyle: relative
  RequiredDisclaimer: "Grounding disclaimer text"
"""
    temp_skill_config(content)
    
    assistant = ReviewConversationAssistant()
    res = assistant.answer("What is Location 920?", None)
    
    assert "Grounding disclaimer text" in res
    assert "file:///" not in res


def test_tool_permission_denial(temp_skill_config):
    """Verifies that if a tool has intents removed from the skill file, permissions are denied."""
    mock_skill_content = """---
name: restricted_skill
version: 1.0.0
description: restricted
role: restricted
capabilities:
  - dataframe_lookup
  - documentation_rag
---
# Configuration

## Objectives
- Restrict things.

## Available Tools
- Name: classification_tool
  Intents: []
  Mutating: false
  RequiredDataframe: true
- Name: eligibility_tool
  Intents: ["row_explanation"]
  Mutating: false
  RequiredDataframe: true
- Name: allocation_tool
  Intents: ["row_explanation"]
  Mutating: false
  RequiredDataframe: true
- Name: RAG_retriever
  Intents: ["rag"]
  Mutating: false
  RequiredDataframe: false
  RequiredGrounding: true

## Routing Policies
- Match "Explain" -> intent: row_explanation

## Refusal Policies
- Matches: ["refuse"]
  RefusalResponse: "No"

## Grounding & Citation Policies
- StrictGrounding: true
  OmitProtocols: []
  RequiredDisclaimer: "Grounding disclaimer"
"""
    temp_skill_config(mock_skill_content)
    
    assistant = ReviewConversationAssistant()
    df = pd.DataFrame([{"Trans Ref": "12345", "Vendor Name": "Test"}])
    
    res = assistant.answer("explain transaction 12345", df)
    assert "Tool permission denied: classification_tool is not permitted for intent 'row_explanation'." in res


def test_no_root_skill_modification():
    """Ensures that the real root SKILL.md file is untouched during the test run."""
    assert os.path.exists("SKILL.md"), "Root SKILL.md must exist."
    with open("SKILL.md", "r", encoding="utf-8") as f:
        content_before = f.read()

    # Perform a dummy temp skill load
    orig_env = os.environ.get("BOC_SKILL_FILE_PATH")
    os.environ["BOC_SKILL_FILE_PATH"] = "dummy_nonexistent.md"
    
    # Restore env
    if orig_env is not None:
        os.environ["BOC_SKILL_FILE_PATH"] = orig_env
    else:
        os.environ.pop("BOC_SKILL_FILE_PATH", None)

    with open("SKILL.md", "r", encoding="utf-8") as f:
        content_after = f.read()
        
    assert content_before == content_after, "Root SKILL.md was modified during test run!"

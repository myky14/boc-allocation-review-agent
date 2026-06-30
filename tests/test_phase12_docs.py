import os
import re
from pathlib import Path
import pytest

PHASE12_FILES = [
    "docs/phase12_adk_feasibility.md",
    "docs/phase12_runtime_mapping.md",
    "docs/phase12_migration_risks.md",
    "docs/phase12_implementation_plan.md",
    "docs/phase12_poc_checklist.md"
]

# Unsafe and Safe ADK Regexes
UNSAFE_ADK = [
    re.compile(r'\b(?:native\s+)?(?:google\s+)?adk\s+(?:runtime\s+)?(?:\w+\s+){0,3}(?:implemented|deployed|active|live|integrated)\b', re.IGNORECASE),
]
SAFE_ADK = [
    re.compile(r'\b(?:google\s+|native\s+)?adk\s+inspired\b', re.IGNORECASE),
    re.compile(r'\b(?:google\s+|native\s+)?adk\s+(?:\w+\s+){0,3}(?:is\s+)?not\s+implemented\b', re.IGNORECASE),
    re.compile(r'\bnot\s+implement\s+(?:native\s+)?adk\b', re.IGNORECASE),
    re.compile(r'\bno\s+native\s+adk\b', re.IGNORECASE),
    re.compile(r'\bnative\s+(?:google\s+)?adk\s+remains\s+(?:\w+\s+){0,3}(?:future\s+)?optional\s+work\b', re.IGNORECASE),
    re.compile(r'\bwrapper\s+poc\b', re.IGNORECASE),
    re.compile(r'\bproof\s+of\s+concept\b', re.IGNORECASE),
    re.compile(r'\bconcept\s+only\b', re.IGNORECASE),
    re.compile(r'\b(?:future|optional|planned)\s+(?:\w+\s+){0,3}(?:migration|wrapper)\b', re.IGNORECASE),
]

# Unsafe and Safe Vertex Regexes
UNSAFE_VERTEX = [
    re.compile(r'\bvertex\s+ai\s+(?:agent\s+engine\s+)?(?:\w+\s+){0,3}(?:deployed|integrated|active|live|implemented)\b', re.IGNORECASE),
]
SAFE_VERTEX = [
    re.compile(r'\bvertex\s+ai\s+(?:migration\s+is\s+)?optional\b', re.IGNORECASE),
    re.compile(r'\bvertex\s+ai\s+(?:is\s+)?not\s+(?:deployed|implemented)\b', re.IGNORECASE),
    re.compile(r'\bno\s+vertex\s+ai\b', re.IGNORECASE),
    re.compile(r'\b(?:future|optional|planned)\s+vertex\s+ai\b', re.IGNORECASE),
]

# Unsafe and Safe Agent Engine Regexes
UNSAFE_AGENT_ENGINE = [
    re.compile(r'\bagent\s+engine\b', re.IGNORECASE),
]
SAFE_AGENT_ENGINE = [
    re.compile(r'\b(?:vertex\s+ai\s+|gemini\s+)?agent\s+engine\s+(?:services\s+)?(?:\w+\s+){0,5}not\s+(?:deployed|implemented|active)\b', re.IGNORECASE),
    re.compile(r'\b(?:future|optional|planned|conceptual|potential)\s+(?:\w+\s+){0,10}agent\s+engine\b', re.IGNORECASE),
    re.compile(r'\bagent\s+engine\s+config\b', re.IGNORECASE),
    re.compile(r'\b(?:delete|rollback|deploy|export|wrap)\s+(?:\w+\s+){0,10}agent\s+engine\b', re.IGNORECASE),
    re.compile(r'\bdependency\s+on\s+(?:\w+\s+){0,5}agent\s+engine\b', re.IGNORECASE),
    re.compile(r'\bmigrat\w*\s+to\s+(?:\w+\s+){0,10}agent\s+engine\b', re.IGNORECASE),
    re.compile(r'\bno\s+agent\s+engine\b', re.IGNORECASE),
]

# Unsafe and Safe Gemini Regexes
UNSAFE_GEMINI = [
    re.compile(r'\bgemini\s+(?:integration\s+)?(?:is\s+)?(?:\w+\s+){0,3}(?:live|active|deployed|integrated|implemented)\b', re.IGNORECASE),
]
SAFE_GEMINI = [
    re.compile(r'\bgemini\s+(?:\w+\s+){0,3}(?:is\s+)?not\s+(?:integrated|implemented|deployed)\b', re.IGNORECASE),
    re.compile(r'\bno\s+gemini\s+integration\b', re.IGNORECASE),
    re.compile(r'\b(?:future|optional|planned)\s+gemini\b', re.IGNORECASE),
]

# Unsafe and Safe Allocation LLM Regexes
UNSAFE_ALLOCATION_LLM = [
    re.compile(r'\bgemini\s+(?:powers|determines|approves|decides)\b', re.IGNORECASE),
    re.compile(r'\bllm\s+(?:\w+\s+){0,3}(?:determines|approves|decides)\b', re.IGNORECASE),
    re.compile(r'\bai\s+(?:\w+\s+){0,3}(?:determines|approves|decides)\b', re.IGNORECASE),
]
SAFE_ALLOCATION_LLM = [
    re.compile(r'\bgemini\s+must\s+not\s+make\b', re.IGNORECASE),
    re.compile(r'\bgemini\s+must\s+not\s+decide\b', re.IGNORECASE),
    re.compile(r'\bnot\s+make\s+final\b', re.IGNORECASE),
    re.compile(r'\bdoes\s+not\s+delegate\b', re.IGNORECASE),
    re.compile(r'\bno\s+decision\b', re.IGNORECASE),
    re.compile(r'\bexplanation\b', re.IGNORECASE),
    re.compile(r'\bexplain\b', re.IGNORECASE),
]

# Unsafe and Safe Production Platform/Compliance Regexes
UNSAFE_PRODUCTION_PLATFORM = [
    re.compile(r'\bproduction\s+(?:grade\s+)?tax\s+(?:filing\s+)?platform\b', re.IGNORECASE),
    re.compile(r'\bofficial\s+(?:compliance|cra|cavco)\s+(?:engine|platform|determination)\b', re.IGNORECASE),
    re.compile(r'\bofficial\s+statutory\s+determination\b', re.IGNORECASE),
]
SAFE_PRODUCTION_PLATFORM = [
    re.compile(r'\breview\s+support\b', re.IGNORECASE),
    re.compile(r'\blocal\s+deterministic\b', re.IGNORECASE),
    re.compile(r'\blocal\s+first\b', re.IGNORECASE),
    re.compile(r'\bsynthetic\s+workflow\b', re.IGNORECASE),
    re.compile(r'\bportfolio\s+ready\b', re.IGNORECASE),
    re.compile(r'\bnot\s+an\s+official\b', re.IGNORECASE),
]

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def split_into_sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r'\n+|(?<=[.!?])\s+', text) if s.strip()]

def check_match_with_safety(norm_text: str, unsafe_list: list, safe_list: list) -> bool:
    unsafe_matches = []
    for r in unsafe_list:
        for m in r.finditer(norm_text):
            unsafe_matches.append((m.start(), m.end()))
            
    if not unsafe_matches:
        return False
        
    safe_matches = []
    for r in safe_list:
        for m in r.finditer(norm_text):
            safe_matches.append((m.start(), m.end()))
            
    for u_start, u_end in unsafe_matches:
        covered = False
        for s_start, s_end in safe_matches:
            if s_start <= u_start and s_end >= u_end:
                covered = True
                break
        if not covered:
            return True
    return False

def contains_false_native_adk_claim(text: str) -> bool:
    return any(check_match_with_safety(normalize_text(s), UNSAFE_ADK, SAFE_ADK) for s in split_into_sentences(text))

def contains_false_vertex_claim(text: str) -> bool:
    return any(check_match_with_safety(normalize_text(s), UNSAFE_VERTEX, SAFE_VERTEX) for s in split_into_sentences(text))

def contains_false_gemini_claim(text: str) -> bool:
    return any(check_match_with_safety(normalize_text(s), UNSAFE_GEMINI, SAFE_GEMINI) for s in split_into_sentences(text))

def contains_false_agent_engine_claim(text: str) -> bool:
    return any(check_match_with_safety(normalize_text(s), UNSAFE_AGENT_ENGINE, SAFE_AGENT_ENGINE) for s in split_into_sentences(text))

def contains_false_allocation_llm_claim(text: str) -> bool:
    return any(check_match_with_safety(normalize_text(s), UNSAFE_ALLOCATION_LLM, SAFE_ALLOCATION_LLM) for s in split_into_sentences(text))

def contains_false_production_platform_claim(text: str) -> bool:
    return any(check_match_with_safety(normalize_text(s), UNSAFE_PRODUCTION_PLATFORM, SAFE_PRODUCTION_PLATFORM) for s in split_into_sentences(text))

def contains_false_phase12_claim(text: str) -> bool:
    return (
        contains_false_native_adk_claim(text) or
        contains_false_vertex_claim(text) or
        contains_false_gemini_claim(text) or
        contains_false_agent_engine_claim(text) or
        contains_false_allocation_llm_claim(text) or
        contains_false_production_platform_claim(text)
    )

def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def test_phase12_files_exist():
    for f in PHASE12_FILES:
        assert os.path.exists(f), f"{f} is missing"

def test_readme_links_to_phase12():
    readme = read_file("README.md")
    for f in PHASE12_FILES:
        assert f in readme, f"README.md does not reference {f}"

def test_claims_restrictor_phase12():
    for f in PHASE12_FILES:
        content = read_file(f)
        if contains_false_phase12_claim(content):
            raise AssertionError(f"Unsafe false claim detected in Phase 12 file: {f}")

def test_no_forbidden_patterns_in_phase12():
    for filepath in PHASE12_FILES:
        content = read_file(filepath)
        assert "file:///" not in content, f"prohibited file:/// link in {filepath}"
        
        # No absolute local paths
        assert not re.search(r'\b[a-zA-Z]:[\\/]', content), f"Windows drive path detected in {filepath}"
        assert not re.search(r'\\\\[a-zA-Z0-9_\.\-]+\\', content), f"UNC path detected in {filepath}"
        assert not re.search(r'\b/(?:users|home|root|mnt|var|opt)\b', content), f"POSIX absolute path detected in {filepath}"

# --- Table-Driven Tests for Safe/Unsafe Claims ---

@pytest.mark.parametrize("text", [
    "Future migration is documented. Native Google ADK has been implemented.",
    "Future roadmap exists. Vertex AI has been deployed.",
    "Gemini integration is optional. Gemini determines allocations.",
    "The wrapper is planned, but Gemini approves tax eligibility.",
    "The migration is conceptual. The Cloud runtime uses Agent Engine.",
    "The design is optional. AI automatically decides allocations.",
    "Native ADK migration is planned, but Native Google ADK has been implemented."
])
def test_contains_false_phase12_claim_flags_unsafe(text):
    assert contains_false_phase12_claim(text)

@pytest.mark.parametrize("text", [
    "Native ADK migration is planned.",
    "ADK-inspired runtime.",
    "No native Google ADK implementation.",
    "Vertex AI is not deployed.",
    "Gemini integration is not implemented.",
    "Wrapper proof of concept.",
    "Local deterministic allocation engine.",
    "Synthetic review workflow.",
    "Review support only."
])
def test_contains_false_phase12_claim_allows_safe(text):
    assert not contains_false_phase12_claim(text)

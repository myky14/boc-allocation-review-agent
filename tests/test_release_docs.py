import os
import re
from pathlib import Path
import pytest

# Paths to scan for claims and release validation
RELEASE_DOCS = [
    "README.md",
    "CHANGELOG.md",
    "docs/github_release_draft.md",
    "docs/portfolio_publishing_checklist.md",
    "docs/recruiter_quickstart.md",
    "docs/project_pitch.md",
    "docs/final_qa_checklist.md"
]

# Expanded list for markdown link and image validations
ALL_DOCS_FOR_LINK_VALIDATION = [
    "README.md",
    "CHANGELOG.md",
    "docs/github_release_draft.md",
    "docs/portfolio_publishing_checklist.md",
    "docs/recruiter_quickstart.md",
    "docs/project_pitch.md",
    "docs/final_qa_checklist.md",
    "docs/runtime_architecture.md",
    "docs/evaluation_plan.md",
    "docs/architecture.md",
    "walkthrough.md",
    "PROJECT_CONTEXT.md"
]

# Regex boundaries
WINDOWS_DRIVE_PATTERN = re.compile(r'\b[a-zA-Z]:[\\/]')
UNC_PATH_PATTERN = re.compile(r'\\\\[a-zA-Z0-9_\.\-]+\\')
POSIX_PATH_PATTERN = re.compile(r'\b/(?:users|home|root|mnt|var|opt)\b')

# Unsafe release patterns
UNSAFE_RELEASE = [
    re.compile(r'\bgithub\s+release\s+(?:\w+\s+){0,3}(?:published|live|exists)\b'),
    re.compile(r'\brelease\s+(?:\w+\s+){0,3}(?:published|live)\b'),
    re.compile(r'\bv2\s+0\s+0\s+portfolio\s+(?:\w+\s+){0,3}released\b'),
]

SAFE_RELEASE = [
    re.compile(r'\bgithub\s+release\s+draft\b'),
    re.compile(r'\brelease\s+draft\b'),
    re.compile(r'\bdraft\s+release\b'),
    re.compile(r'\bsuggested\s+(?:release\s+)?tag\b'),
    re.compile(r'\bplanned\s+release\b'),
    re.compile(r'\bpublish\s+(?:the\s+)?release\b'),
    re.compile(r'\bnot\s+published\b'),
    re.compile(r'\bhas\s+not\s+been\s+published\b'),
    re.compile(r'\brelease\s+has\s+not\s+been\s+published\b'),
]

# Unsafe Cloud Run patterns
UNSAFE_CLOUD_RUN = [
    re.compile(r'\bcloud\s+run\s+service\s+(?:\w+\s+){0,3}(?:active|live|running)\b'),
    re.compile(r'\bcloud\s+run\s+deployment\s+(?:\w+\s+){0,3}(?:active|live|exists)\b'),
    re.compile(r'\bdeployed\s+to\s+cloud\s+run\b'),
    re.compile(r'\b(?:running|runs|hosted|live)\s+on\s+cloud\s+run\b'),
]

# Safe Cloud Run patterns
SAFE_CLOUD_RUN = [
    re.compile(r'\bcloud\s+run\s+deployment\s+readiness\b'),
    re.compile(r'\bcloud\s+run\s+deployment\s+guide\b'),
    re.compile(r'\bready\s+for\s+cloud\s+run\s+deployment\b'),
    re.compile(r'\bnot\s+(?:currently\s+)?deployed\s+to\s+cloud\s+run\b'),
    re.compile(r'\bfuture\s+cloud\s+run\s+deployment\b'),
    re.compile(r'\boptional\s+cloud\s+run\s+deployment\b'),
]

# Unsafe AI integration patterns
UNSAFE_AI = [
    re.compile(r'\b(?:google\s+|native\s+)?adk\s+(?:\w+\s+){0,3}(?:implemented|active|deployed|live)\b'),
    re.compile(r'\bvertex\s+ai\s+(?:\w+\s+){0,3}(?:active|integrated|implemented|deployed|live)\b'),
    re.compile(r'\bgemini\s+(?:\w+\s+){0,3}(?:active|integrated|implemented|deployed|live)\b'),
]

# Safe AI integration patterns
SAFE_AI = [
    re.compile(r'\b(?:google\s+|native\s+)?adk\s+inspired\b'),
    re.compile(r'\b(?:google\s+|native\s+)?adk\s+(?:is\s+)?not\s+implemented\b'),
    re.compile(r'\bnative\s+(?:google\s+)?adk\s+remains\s+future\s+optional\s+work\b'),
    re.compile(r'\bvertex\s+ai\s+migration\s+is\s+optional\b'),
    re.compile(r'\bvertex\s+ai\s+migration\b'),
    re.compile(r'\bvertex\s+ai\s+(?:is\s+)?not\s+deployed\b'),
    re.compile(r'\bgemini\s+(?:is\s+)?not\s+integrated\b'),
    re.compile(r'\bno\s+vertex\s+or\s+gemini\s+runtime\s+integration\s+(?:is\s+)?(?:implemented)?\b'),
]

# Unsafe compliance patterns
UNSAFE_COMPLIANCE = [
    re.compile(r'\bproduction\s+grade\s+(?:\w+\s+){0,3}tax\b'),
    re.compile(r'\bproduction\s+tax\s+filing\b'),
    re.compile(r'\bofficial\s+(?:\w+\s+){0,3}compliance\b'),
    re.compile(r'\bofficial\s+(?:\w+\s+){0,3}source\s+of\s+truth\b'),
    re.compile(r'\bproduction\s+(?:\w+\s+){0,3}filing\s+system\b'),
]

# Safe compliance patterns
SAFE_COMPLIANCE = [
    re.compile(r'\breview\s+support\b'),
    re.compile(r'\bnot\s+(?:an\s+)?official\s+tax\s+or\s+legal\s+determination\b'),
    re.compile(r'\bnot\s+(?:an\s+)?official\s+filing\s+system\b'),
    re.compile(r'\bnot\s+(?:an\s+)?official\s+compliance\b'),
    re.compile(r'\binternal\s+synthetic\s+review\b'),
    re.compile(r'\bsource\s+of\s+truth\s+for\s+this\s+repository\s+s\s+synthetic\s+review\s+workflow\b'),
]

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def read_doc(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def iter_release_docs() -> list[Path]:
    return [Path(p) for p in RELEASE_DOCS]

def iter_all_link_docs() -> list[Path]:
    return [Path(p) for p in ALL_DOCS_FOR_LINK_VALIDATION]

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

def contains_false_release_claim(text: str) -> bool:
    norm = normalize_text(text)
    return check_match_with_safety(norm, UNSAFE_RELEASE, SAFE_RELEASE)

def contains_false_cloud_run_claim(text: str) -> bool:
    norm = normalize_text(text)
    return check_match_with_safety(norm, UNSAFE_CLOUD_RUN, SAFE_CLOUD_RUN)

def contains_false_ai_integration_claim(text: str) -> bool:
    norm = normalize_text(text)
    return check_match_with_safety(norm, UNSAFE_AI, SAFE_AI)

def contains_false_compliance_claim(text: str) -> bool:
    norm = normalize_text(text)
    return check_match_with_safety(norm, UNSAFE_COMPLIANCE, SAFE_COMPLIANCE)

def test_release_docs_exist():
    # 1. release docs exist
    for doc in iter_release_docs():
        assert doc.exists(), f"Release doc {doc} does not exist"

def test_readme_links_to_release_docs():
    # 2. README links to release docs
    readme = normalize_text(read_doc("README.md"))
    assert "github release draft" in readme
    assert "recruiter quickstart" in readme
    assert "portfolio publishing checklist" in readme
    assert "project pitch snippets" in readme
    assert "final qa checklist" in readme

def test_release_draft_version():
    # 3. release draft includes v2.0.0-portfolio
    draft = read_doc("docs/github_release_draft.md")
    assert "v2.0.0-portfolio" in draft

def test_no_false_release_claims():
    # 4. reject false release claims
    for doc in iter_release_docs():
        content = read_doc(doc)
        if contains_false_release_claim(content):
            raise AssertionError(f"Unsafe release claim detected in {doc}")

def test_no_false_cloud_run_claims():
    # 5. reject false Cloud Run deployment claims
    for doc in iter_release_docs():
        content = read_doc(doc)
        if contains_false_cloud_run_claim(content):
            raise AssertionError(f"Unsafe Cloud Run deployment claim detected in {doc}")

def test_no_false_native_claims():
    # 6. reject false native ADK/Vertex/Gemini claims
    for doc in iter_release_docs():
        content = read_doc(doc)
        if contains_false_ai_integration_claim(content):
            raise AssertionError(f"Unsafe native platform claim detected in {doc}")

def test_no_false_compliance_claims():
    # 7. reject false official compliance / tax authority claims
    for doc in iter_release_docs():
        content = read_doc(doc)
        if contains_false_compliance_claim(content):
            raise AssertionError(f"Unsafe tax compliance claim detected in {doc}")

def test_no_prohibited_paths():
    # 8. absolute path detection
    for doc in iter_all_link_docs():
        content = read_doc(doc)
        assert not WINDOWS_DRIVE_PATTERN.search(content), f"Windows drive path detected in {doc}"
        assert not UNC_PATH_PATTERN.search(content), f"UNC path detected in {doc}"
        assert not POSIX_PATH_PATTERN.search(content), f"POSIX absolute path detected in {doc}"
        # Only reject actual links or paths starting with file:/// followed by alphanumeric chars
        assert not re.search(r'file:///[\w]', content), f"prohibited file:/// link/path detected in {doc}"

def test_markdown_links_are_valid():
    # 9. validate markdown links in expanded release/architecture docs
    for doc in iter_all_link_docs():
        content = read_doc(doc)
        links = re.findall(r'\[.*?\]\((.*?)\)', content)
        for link in links:
            if link.startswith("http://") or link.startswith("https://") or link.startswith("#") or not link:
                continue
            assert "file:///" not in link, f"link contains file:/// in {doc}"
            clean_link = link.split("#")[0].split("?")[0]
            if not clean_link:
                continue
            resolved = Path(doc).parent / clean_link
            assert resolved.exists(), f"Link '{link}' in {doc} resolves to missing file '{resolved}'"

def test_markdown_images_are_valid():
    # 10. validate markdown images in expanded release/architecture docs
    for doc in iter_all_link_docs():
        content = read_doc(doc)
        images = re.findall(r'!\[.*?\]\((.*?)\)', content)
        for img in images:
            if img.startswith("http://") or img.startswith("https://") or not img:
                continue
            assert "file:///" not in img, f"image contains file:/// in {doc}"
            clean_img = img.split("#")[0].split("?")[0]
            if not clean_img:
                continue
            resolved = Path(doc).parent / clean_img
            assert resolved.exists(), f"Image link '{img}' in {doc} resolves to missing file '{resolved}'"

def test_test_count_synchronization():
    # 11. test count validation
    stale_counts = ["106", "137", "138", "143", "144", "145", "152", "153", "176", "183", "195"]
    for doc in iter_all_link_docs():
        content = read_doc(doc).lower()
        
        # Verify no stale counts refer to the current suite total
        for count in stale_counts:
            # Match count followed by tests, unit, passed, passing, etc.
            pattern = rf'\b{count}\s*(?:-|\s)(?:unit|passed|passing|test|tests|unit\s+and\s+integration\s+tests)\b'
            if re.search(pattern, content):
                raise AssertionError(f"Stale test count {count} found in {doc}")
                
        # If the file discusses the current suite count, verify it mentions 246
        if doc.name in ["github_release_draft.md", "portfolio_publishing_checklist.md", "recruiter_quickstart.md", "project_pitch.md", "final_qa_checklist.md", "walkthrough.md"]:
            assert "246" in content, f"{doc} must mention 246 test suite count"

def test_final_qa_checklist_realism_and_secret_scanning():
    # 12. final QA checklist realism and secret scanning check
    checklist = read_doc("docs/final_qa_checklist.md").lower()
    
    # Required commands
    assert "pytest" in checklist
    assert "smoke_deployment.py" in checklist
    assert "py_compile app.py" in checklist
    assert "boc_agent.cli" in checklist
    assert "evaluate_outputs.py" in checklist
    assert "build_review_queue.py" in checklist
    assert "git diff boc_agent/tools/allocation_tool.py" in checklist
    assert "git diff --check" in checklist
    
    # Expected metrics
    assert "201" in checklist
    assert "approved" in checklist and "113" in checklist
    assert "needs human review" in checklist and "88" in checklist
    
    # Secret scanning manual verification disclaimer
    assert "manual code and asset audit" in checklist
    assert "no secrets" in checklist

# --- Parameterized Table-Driven Tests ---

@pytest.mark.parametrize("text", [
    "The GitHub release has already been published.",
    "The GitHub release is already live.",
    "The GitHub release exists.",
    "The release has been published.",
    "The release is live.",
    "v2.0.0-portfolio has been released.",
    "v2.0.0-portfolio is released."
])
def test_false_release_claim_detector_flags_unsafe(text):
    assert contains_false_release_claim(text)

@pytest.mark.parametrize("text", [
    "This is a GitHub release draft.",
    "Suggested release tag: v2.0.0-portfolio.",
    "Publish the release after review.",
    "Planned release notes are provided.",
    "The release has not been published."
])
def test_false_release_claim_detector_allows_safe(text):
    assert not contains_false_release_claim(text)

@pytest.mark.parametrize("text", [
    "The Cloud Run service is active.",
    "The Cloud Run deployment is active.",
    "The Cloud Run service is live.",
    "Cloud Run deployment exists.",
    "The app is deployed to Cloud Run.",
    "The service is running on Cloud Run.",
    "The project is hosted on Cloud Run."
])
def test_false_cloud_run_claim_detector_flags_unsafe(text):
    assert contains_false_cloud_run_claim(text)

@pytest.mark.parametrize("text", [
    "Cloud Run deployment readiness is documented.",
    "This is a Cloud Run deployment guide.",
    "The project is ready for Cloud Run deployment.",
    "The project is not deployed to Cloud Run.",
    "Future Cloud Run deployment remains optional."
])
def test_false_cloud_run_claim_detector_allows_safe(text):
    assert not contains_false_cloud_run_claim(text)

@pytest.mark.parametrize("text", [
    "Google ADK has been implemented.",
    "Google ADK is active.",
    "Native Google ADK is deployed.",
    "Vertex AI integration is active.",
    "Vertex AI has been integrated.",
    "Vertex AI Agent Engine is deployed.",
    "Gemini integration is active.",
    "Gemini has been integrated.",
    "Gemini is live."
])
def test_false_ai_integration_claim_detector_flags_unsafe(text):
    assert contains_false_ai_integration_claim(text)

@pytest.mark.parametrize("text", [
    "This project is ADK-inspired.",
    "Google ADK is not implemented.",
    "Native Google ADK remains future optional work.",
    "Vertex AI migration is optional.",
    "Vertex AI is not deployed.",
    "Gemini is not integrated.",
    "No Vertex or Gemini runtime integration is implemented."
])
def test_false_ai_integration_claim_detector_allows_safe(text):
    assert not contains_false_ai_integration_claim(text)

@pytest.mark.parametrize("text", [
    "This is a production-grade tax filing platform.",
    "This is a production tax filing system.",
    "This is an official tax compliance engine.",
    "This provides official CRA compliance.",
    "This provides official CAVCO compliance.",
    "This is an official tax-credit eligibility source of truth."
])
def test_false_compliance_claim_detector_flags_unsafe(text):
    assert contains_false_compliance_claim(text)

@pytest.mark.parametrize("text", [
    "This is an accounting review-support workflow.",
    "This is not an official tax or legal determination.",
    "This is not an official filing system.",
    "It follows internal synthetic review conventions.",
    "The deterministic engine is the source of truth for this repository's synthetic review workflow."
])
def test_false_compliance_claim_detector_allows_safe(text):
    assert not contains_false_compliance_claim(text)

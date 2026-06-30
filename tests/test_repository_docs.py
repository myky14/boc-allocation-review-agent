import os
import re
from pathlib import Path
import pytest

REPO_FILES = [
    "docs/social_preview.md",
    "docs/logo_guidelines.md",
    "docs/architecture_diagram_guide.md",
    "CONTRIBUTING.md",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    ".github/ISSUE_TEMPLATE/bug_report.md",
    ".github/ISSUE_TEMPLATE/feature_request.md",
    ".github/pull_request_template.md",
    "LICENSE"
]

WINDOWS_DRIVE_PATTERN = re.compile(r'\b[a-zA-Z]:[\\/]')
UNC_PATH_PATTERN = re.compile(r'\\\\[a-zA-Z0-9_\.\-]+\\')
POSIX_PATH_PATTERN = re.compile(r'\b/(?:users|home|root|mnt|var|opt)\b')

# Precise unsafe/safe pattern registers
UNSAFE_ADK = [
    re.compile(r'\b(?:google\s+|native\s+)?adk\s+(?:\w+\s+){0,3}(?:implemented|active|deployed|live|integrated)\b', re.IGNORECASE),
]
SAFE_ADK = [
    re.compile(r'\b(?:google\s+|native\s+)?adk\s+inspired\b', re.IGNORECASE),
    re.compile(r'\b(?:google\s+|native\s+)?adk\s+(?:is\s+)?not\s+implemented\b', re.IGNORECASE),
    re.compile(r'\bnative\s+(?:google\s+)?adk\s+remains\s+(?:future\s+)?optional\s+work\b', re.IGNORECASE),
]

UNSAFE_AI = [
    re.compile(r'\bvertex\s+ai\s+(?:\w+\s+){0,3}(?:deployed|active|live|integrated|implemented)\b', re.IGNORECASE),
    re.compile(r'\bgemini\s+(?:integration\s+)?(?:\w+\s+){0,3}(?:active|live|integrated|implemented|deployed)\b', re.IGNORECASE),
]
SAFE_AI = [
    re.compile(r'\bvertex\s+ai\s+migration\s+is\s+optional\b', re.IGNORECASE),
    re.compile(r'\bvertex\s+ai\s+(?:is\s+)?not\s+deployed\b', re.IGNORECASE),
    re.compile(r'\bgemini\s+(?:is\s+)?not\s+integrated\b', re.IGNORECASE),
    re.compile(r'\bno\s+vertex\s+or\s+gemini\s+runtime\s+integration\s+(?:is\s+)?(?:implemented)?\b', re.IGNORECASE),
]

UNSAFE_CLOUD = [
    re.compile(r'\bcloud\s+run\s+deployment\s+(?:\w+\s+){0,3}(?:active|live|exists)\b', re.IGNORECASE),
    re.compile(r'\bdeployed\s+to\s+cloud\s+run\b', re.IGNORECASE),
    re.compile(r'\b(?:running|runs|hosted|live)\s+on\s+cloud\s+run\b', re.IGNORECASE),
    re.compile(r'\bcloud\s+run\s+service\s+(?:\w+\s+){0,3}(?:active|live|running)\b', re.IGNORECASE),
]
SAFE_CLOUD = [
    re.compile(r'\bcloud\s+run\s+deployment\s+readiness\b', re.IGNORECASE),
    re.compile(r'\bready\s+for\s+cloud\s+run\s+deployment\b', re.IGNORECASE),
    re.compile(r'\bnot\s+(?:currently\s+)?deployed\s+to\s+cloud\s+run\b', re.IGNORECASE),
    re.compile(r'\bfuture\s+cloud\s+run\s+deployment\b', re.IGNORECASE),
    re.compile(r'\boptional\s+cloud\s+run\s+deployment\b', re.IGNORECASE),
    re.compile(r'\bcloud\s+run\s+deployment\s+guide\b', re.IGNORECASE),
]

UNSAFE_PRODUCTION = [
    re.compile(r'\bproduction\s+grade\s+(?:\w+\s+){0,3}(?:platform|accounting)\b', re.IGNORECASE),
    re.compile(r'\bproduction\s+accounting\s+platform\b', re.IGNORECASE),
    re.compile(r'\bofficial\s+compliance\s+engine\b', re.IGNORECASE),
    re.compile(r'\bofficial\s+tax\s+compliance\s+platform\b', re.IGNORECASE),
    re.compile(r'\bofficial\s+compliance\s+engine\b', re.IGNORECASE),
]
SAFE_PRODUCTION = [
    re.compile(r'\bportfolio\s+ready\s+review\s+support\s+project\b', re.IGNORECASE),
    re.compile(r'\bnot\s+(?:an\s+)?official\s+tax\s+or\s+legal\s+determination\s+(?:system)?\b', re.IGNORECASE),
]

def normalize_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def split_into_sentences(text: str) -> list[str]:
    # Split by newlines or sentence boundaries (., !, ?)
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

def contains_false_repository_claim(text: str) -> bool:
    sentences = split_into_sentences(text)
    for sentence in sentences:
        norm = normalize_text(sentence)
        if check_match_with_safety(norm, UNSAFE_ADK, SAFE_ADK):
            return True
        if check_match_with_safety(norm, UNSAFE_AI, SAFE_AI):
            return True
        if check_match_with_safety(norm, UNSAFE_CLOUD, SAFE_CLOUD):
            return True
        if check_match_with_safety(norm, UNSAFE_PRODUCTION, SAFE_PRODUCTION):
            return True
    return False

def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def test_repo_docs_exist():
    # 1. new files exist
    for f in REPO_FILES:
        assert os.path.exists(f), f"File {f} does not exist"

def test_contributing_references_pytest():
    # 2. CONTRIBUTING.md references pytest
    content = read_file("CONTRIBUTING.md")
    assert "pytest" in content.lower(), "CONTRIBUTING.md must mention pytest"

def test_security_references_synthetic_data():
    # 3. SECURITY.md references synthetic data
    content = read_file("SECURITY.md")
    assert "synthetic data" in content.lower(), "SECURITY.md must mention synthetic data"

def test_code_of_conduct_exists():
    # 4. CODE_OF_CONDUCT.md exists
    assert os.path.exists("CODE_OF_CONDUCT.md"), "CODE_OF_CONDUCT.md does not exist"

def test_issue_templates_exist():
    # 5. Issue templates exist
    assert os.path.exists(".github/ISSUE_TEMPLATE/bug_report.md")
    assert os.path.exists(".github/ISSUE_TEMPLATE/feature_request.md")

def test_pr_template_exists():
    # 6. PR template exists
    assert os.path.exists(".github/pull_request_template.md")

def test_claims_restrictor():
    # 7. no false claims committed in the new presentation files
    for f in REPO_FILES:
        content = read_file(f)
        if contains_false_repository_claim(content):
            raise AssertionError(f"Unsafe false claim detected in {f}")

def test_relative_links_resolve():
    # 8. validate relative links in new files
    for filepath in REPO_FILES:
        content = read_file(filepath)
        links = re.findall(r'\[.*?\]\((.*?)\)', content)
        for link in links:
            if link.startswith("http://") or link.startswith("https://") or link.startswith("#") or not link:
                continue
            assert "file:///" not in link, f"link contains file:/// in {filepath}"
            clean_link = link.split("#")[0].split("?")[0]
            if not clean_link:
                continue
            resolved = Path(filepath).parent / clean_link
            assert resolved.exists(), f"Link '{link}' in {filepath} resolves to missing file '{resolved}'"

def test_no_file_links():
    # 9. validate no file:/// links in new files
    for filepath in REPO_FILES:
        content = read_file(filepath)
        assert not re.search(r'file:///[\w]', content), f"prohibited file:/// link in {filepath}"

def test_no_missing_images():
    # 10. validate no missing markdown images in new files
    for filepath in REPO_FILES:
        content = read_file(filepath)
        images = re.findall(r'!\[.*?\]\((.*?)\)', content)
        for img in images:
            if img.startswith("http://") or img.startswith("https://") or not img:
                continue
            assert "file:///" not in img, f"image contains file:/// in {filepath}"
            clean_img = img.split("#")[0].split("?")[0]
            if not clean_img:
                continue
            resolved = Path(filepath).parent / clean_img
            assert resolved.exists(), f"Image '{img}' in {filepath} resolves to missing file '{resolved}'"

def test_no_absolute_local_paths():
    # 11. validate no absolute local paths in new files
    for filepath in REPO_FILES:
        content = read_file(filepath)
        assert not WINDOWS_DRIVE_PATTERN.search(content), f"Windows drive path detected in {filepath}"
        assert not UNC_PATH_PATTERN.search(content), f"UNC path detected in {filepath}"
        assert not POSIX_PATH_PATTERN.search(content), f"POSIX absolute path detected in {filepath}"

def test_readme_links_resolve_correctly():
    # 12. README links to new files resolve correctly
    readme = read_file("README.md")
    # Verify we link to these files in the README
    assert "LICENSE" in readme
    assert "CONTRIBUTING.md" in readme
    assert "CODE_OF_CONDUCT.md" in readme
    assert "SECURITY.md" in readme

# --- Table-Driven Tests for Safe/Unsafe Claims ---

@pytest.mark.parametrize("text", [
    "Google ADK has been implemented.",
    "Native Google ADK is deployed.",
    "Vertex AI has been deployed.",
    "Vertex AI integration is active.",
    "Gemini has been integrated.",
    "Gemini integration is active.",
    "Cloud Run deployment is active.",
    "The app is hosted on Cloud Run.",
    "The service is running on Cloud Run.",
    "This is a production-grade accounting platform.",
    "This is a production accounting platform.",
    "This is an official compliance engine.",
    "This is an official tax compliance platform.",
    "Future roadmap is documented. Google ADK has been implemented.",
    "Optional migration is documented, but Gemini integration is active.",
    "Cloud Run readiness is documented, but the service is running on Cloud Run.",
    "No native deployment is implemented, but Vertex AI has been deployed."
])
def test_contains_false_repository_claim_flags_unsafe(text):
    assert contains_false_repository_claim(text)

@pytest.mark.parametrize("text", [
    "This project is ADK-inspired.",
    "Google ADK is not implemented.",
    "Native Google ADK remains optional future work.",
    "Vertex AI migration is optional.",
    "Vertex AI is not deployed.",
    "Gemini is not integrated.",
    "No Vertex or Gemini runtime integration is implemented.",
    "Cloud Run deployment readiness is documented.",
    "This project is ready for Cloud Run deployment.",
    "This project is not deployed to Cloud Run.",
    "This is a portfolio-ready review-support project.",
    "This is not an official tax or legal determination system."
])
def test_contains_false_repository_claim_allows_safe(text):
    assert not contains_false_repository_claim(text)

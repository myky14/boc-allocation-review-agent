import os
import re
import pytest

# Windows absolute paths (e.g. C:\ or C:/ or D:\ or d:/)
WINDOWS_PATH_PATTERN = re.compile(r'\b[a-zA-Z]:[\\/]')
# UNC paths (e.g. \\server\ or \\127.0.0.1\)
UNC_PATH_PATTERN = re.compile(r'\\\\[a-zA-Z0-9_\.\-]+\\')
# file URI (e.g. file:///)
FILE_URI_PATTERN = re.compile(r'file:///')
# POSIX absolute paths starting with specific directories
POSIX_PATH_PATTERN = re.compile(r'\b/(?:users|home|root|mnt|var|opt)\b')

# Unsafe deployment regexes
UNSAFE_REGEXES = [
    re.compile(r'\bcloud\s+run\s+deployment\s+(?:is\s+)?(?:currently\s+)?(?:active|live|exists)\b'),
    re.compile(r'\bcloud\s+run\s+(?:is\s+|has\s+been\s+|currently\s+)?deployed\b'),
    re.compile(r'\bdeployed\s+to\s+cloud\s+run\b'),
    re.compile(r'\bhosted\s+on\s+cloud\s+run\b'),
    re.compile(r'\b(?:running|runs|live)\s+on\s+cloud\s+run\b'),
    re.compile(r'\bcurrently\s+deployed\b'),
    re.compile(r'\bcurrently\s+running\s+on\s+cloud\s+run\b'),
    re.compile(r'\bcurrently\s+runs\s+on\s+cloud\s+run\b'),
]

# Safe deployment regexes
SAFE_REGEXES = [
    re.compile(r'\bnot\s+deployed\s+to\s+cloud\s+run\b'),
    re.compile(r'\bnot\s+currently\s+deployed\s+to\s+cloud\s+run\b'),
    re.compile(r'\bhas\s+not\s+been\s+deployed\s+to\s+cloud\s+run\b'),
    re.compile(r'\bdoes\s+not\s+deploy\s+to\s+cloud\s+run\b'),
    re.compile(r'\bfuture\s+cloud\s+run\s+deployment\b'),
    re.compile(r'\boptional\s+cloud\s+run\s+deployment\b'),
    re.compile(r'\bcloud\s+run\s+deployment\s+readiness\b'),
    re.compile(r'\bcloud\s+run\s+deployment\s+guide\b'),
    re.compile(r'\bready\s+for\s+cloud\s+run\s+deployment\b'),
    re.compile(r'\bcloud\s+run\s+ready\s+documentation\b'),
    re.compile(r'\bdeployment\s+guide\s+only\b'),
]

def normalize_text(text: str) -> str:
    # lowercase
    text = text.lower()
    # replace punctuation with spaces
    text = re.sub(r'[^a-z0-9]', ' ', text)
    # collapse whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def split_into_sentences(text: str) -> list[str]:
    # Split by sentence endings (., !, ?, \n)
    sentences = re.split(r'[\.!\?\n]+', text)
    return [s.strip() for s in sentences if s.strip()]

def contains_active_cloud_run_claim(text: str) -> bool:
    norm = normalize_text(text)
    
    # Find all matches of unsafe regexes
    unsafe_matches = []
    for r in UNSAFE_REGEXES:
        for m in r.finditer(norm):
            unsafe_matches.append((m.start(), m.end(), m.group(0)))
            
    if not unsafe_matches:
        return False
        
    # Find all matches of safe regexes
    safe_matches = []
    for r in SAFE_REGEXES:
        for m in r.finditer(norm):
            safe_matches.append((m.start(), m.end()))
            
    # For every unsafe match, verify it is covered by at least one safe match
    for u_start, u_end, u_str in unsafe_matches:
        covered = False
        for s_start, s_end in safe_matches:
            # Overlap criteria: safe match contains the unsafe match
            if s_start <= u_start and s_end >= u_end:
                covered = True
                break
        if not covered:
            return True
            
    return False

def test_demo_assets_exist():
    # Verify assets directory structure and placeholder .gitkeep files exist
    assert os.path.exists("assets/screenshots/.gitkeep")
    assert os.path.exists("assets/gifs/.gitkeep")
    assert os.path.exists("assets/videos/.gitkeep")
    assert os.path.exists("assets/diagrams/.gitkeep")
    
    # Verify main documentation files exist
    assert os.path.exists("assets/README.md")
    assert os.path.exists("docs/screenshot_checklist.md")
    assert os.path.exists("docs/video_recording_guide.md")
    assert os.path.exists("docs/demo_assets_guide.md")
    assert os.path.exists("docs/presentation_flow.md")

def test_readme_links_to_new_docs():
    with open("README.md", "r", encoding="utf-8") as f:
        readme = f.read().lower()
    
    assert "screenshot_checklist.md" in readme
    assert "video_recording_guide.md" in readme
    assert "demo_assets_guide.md" in readme

def test_guides_recommend_synthetic_data_and_warn_against_exposing_secrets():
    guides = [
        "assets/README.md",
        "docs/screenshot_checklist.md",
        "docs/video_recording_guide.md",
        "docs/demo_assets_guide.md",
        "docs/presentation_flow.md"
    ]
    
    for filepath in guides:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
        # Verify recommendation for synthetic data
        assert ("synthetic data" in content or "synthetic dataset" in content), f"Guide {filepath} must recommend synthetic data only"
        
        # Verify warning against exposing secrets/credentials/billing accounts
        has_secret_warning = any(term in content for term in [
            "credential", "secret", "private data", "local path", "billing", "token", "password"
        ])
        assert has_secret_warning, f"Guide {filepath} must warn against exposing secrets, credentials, or billing accounts"

def test_no_false_claims_of_existing_assets_or_active_deployment():
    guides = [
        "assets/README.md",
        "docs/screenshot_checklist.md",
        "docs/video_recording_guide.md",
        "docs/demo_assets_guide.md",
        "docs/presentation_flow.md",
        "README.md"
    ]
    
    for filepath in guides:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Reject claims that assets already exist
        normalized = normalize_text(content)
        assert "see screenshot below" not in normalized, f"Forbidden asset claim 'see screenshot below' found in {filepath}"
        assert "the following image" not in normalized, f"Forbidden asset claim 'the following image' found in {filepath}"
        assert "as shown below" not in normalized, f"Forbidden asset claim 'as shown below' found in {filepath}"
        
        # Split into sentences and check for active deployment claims
        sentences = split_into_sentences(content)
        for sentence in sentences:
            if contains_active_cloud_run_claim(sentence):
                raise AssertionError(f"False Cloud Run deployment claim detected in sentence: '{sentence}' in file {filepath}")

@pytest.mark.parametrize("text", [
    "Cloud Run deployment is active.",
    "Cloud Run deployment is currently active.",
    "Cloud Run deployment is live.",
    "Cloud Run deployment exists.",
    "Cloud Run is deployed.",
    "Cloud Run has been deployed.",
    "The app is deployed to Cloud Run.",
    "The known app is deployed to Cloud Run.",
    "The demo is hosted on Cloud Run.",
    "The service is running on Cloud Run.",
    "The service is currently running on Cloud Run.",
    "This project currently runs on Cloud Run.",
    "This project is live on Cloud Run.",
    "Cloud Run deployment readiness is documented, but the app is deployed to Cloud Run.",
    "The Cloud Run deployment guide is available, but the demo is hosted on Cloud Run.",
    "This project is ready for Cloud Run deployment; however, it is currently running on Cloud Run.",
    "Future Cloud Run deployment is optional, but the current service is live on Cloud Run.",
    "This project is not deployed to Cloud Run, but another sentence says it is running on Cloud Run."
])
def test_active_cloud_run_claim_detector_flags_unsafe(text):
    assert contains_active_cloud_run_claim(text)

@pytest.mark.parametrize("text", [
    "Cloud Run deployment readiness.",
    "Cloud Run deployment guide.",
    "Cloud Run ready documentation.",
    "This project is ready for Cloud Run deployment.",
    "This project is not deployed to Cloud Run.",
    "This project is not currently deployed to Cloud Run.",
    "This project has not been deployed to Cloud Run.",
    "This project does not deploy to Cloud Run in Phase 11.2.",
    "Future Cloud Run deployment is optional.",
    "Optional Cloud Run deployment remains future work.",
    "Cloud Run deployment is documented as a guide only.",
    "Cloud Run deployment readiness is documented.",
    "The Cloud Run deployment guide explains future options."
])
def test_active_cloud_run_claim_detector_allows_safe(text):
    assert not contains_active_cloud_run_claim(text)

def test_no_markdown_image_embeds_referencing_missing_files():
    # Issue 3: Markdown image path resolution relative to document directory
    guides = [
        "assets/README.md",
        "docs/screenshot_checklist.md",
        "docs/video_recording_guide.md",
        "docs/demo_assets_guide.md",
        "docs/presentation_flow.md",
        "README.md"
    ]
    
    for filepath in guides:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Look for markdown image embeds: ![caption](path)
        embeds = re.findall(r'!\[.*?\]\((.*?)\)', content)
        for path in embeds:
            if path.startswith("http://") or path.startswith("https://"):
                continue
            # Strip anchors or queries if any
            clean_path = path.split("#")[0].split("?")[0]
            
            # Resolve image paths relative to the markdown file's own directory
            dir_name = os.path.dirname(filepath)
            resolved_path = os.path.join(dir_name, clean_path) if dir_name else clean_path
            
            assert os.path.exists(resolved_path), f"Markdown image embed references missing file '{resolved_path}' resolved relative to {filepath}"

def test_no_html_img_tags():
    guides = [
        "assets/README.md",
        "docs/screenshot_checklist.md",
        "docs/video_recording_guide.md",
        "docs/demo_assets_guide.md",
        "docs/presentation_flow.md",
        "README.md"
    ]
    
    for filepath in guides:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
        assert "<img" not in content, f"HTML img tags are prohibited in {filepath}"

def test_no_local_absolute_paths():
    # Issue 4: Regex-based absolute path detection covering Windows, UNC, file URI, and POSIX dirs
    guides = [
        "assets/README.md",
        "docs/screenshot_checklist.md",
        "docs/video_recording_guide.md",
        "docs/demo_assets_guide.md",
        "docs/presentation_flow.md",
        "README.md"
    ]
    
    for filepath in guides:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().lower()
            
        assert not WINDOWS_PATH_PATTERN.search(content), f"Windows absolute path detected in {filepath}"
        assert not UNC_PATH_PATTERN.search(content), f"UNC absolute path detected in {filepath}"
        assert not FILE_URI_PATTERN.search(content), f"File URI absolute path detected in {filepath}"
        assert not POSIX_PATH_PATTERN.search(content), f"POSIX absolute path detected in {filepath}"

import os
import subprocess
import pytest
from scripts.smoke_deployment import main as smoke_main

def test_dockerfile_exists_and_valid():
    dockerfile_path = "Dockerfile"
    assert os.path.exists(dockerfile_path), "Dockerfile must exist at the root"
    
    with open(dockerfile_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Exposes or uses port 8080
    assert "8080" in content, "Dockerfile should refer to port 8080"
    
    # Runs Streamlit with 0.0.0.0
    assert "0.0.0.0" in content, "Dockerfile must bind Streamlit to 0.0.0.0"
    
    # Check for streamlit run CMD
    assert "streamlit run" in content, "Dockerfile must run streamlit"

    # Issue 1: Hatchling build cache order
    assert "--no-install-project" in content, "Dockerfile should run uv sync with --no-install-project"
    assert "uv run --no-sync" in content, "Dockerfile command should run with --no-sync"
    
    # Ensure source files COPY occurs AFTER dependency sync
    sync_idx = content.find("uv sync")
    copy_idx = content.find("COPY boc_agent/")
    assert sync_idx != -1 and copy_idx != -1
    assert sync_idx < copy_idx, "Dependency sync must occur before copying source code"

    # Issue 2: Streamlit XSRF and CORS protection (no unsafe disablement flags)
    assert "enableXsrfProtection=false" not in content, "Do not disable Streamlit XSRF protection"
    assert "enableCORS=false" not in content, "Do not disable Streamlit CORS protection"

    # Safety: No hardcoded API keys or secrets
    for line in content.splitlines():
        lower_line = line.lower()
        if "key" in lower_line or "secret" in lower_line or "token" in lower_line:
            # If env var declaration is present, make sure it is not setting a fake/real credential
            if "env" in lower_line:
                assert "=" in line
                var_val = line.split("=", 1)[1].strip()
                # Ensure no raw key/secret is hardcoded
                assert not any(x in var_val.lower() for x in ["aiza", "sk-", "secret_key", "password"]), \
                    f"Possible hardcoded secret found in Dockerfile: {line}"

def test_dockerignore_exists_and_valid():
    dockerignore_path = ".dockerignore"
    assert os.path.exists(dockerignore_path), ".dockerignore must exist at the root"
    
    with open(dockerignore_path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f.read().splitlines() if line.strip() and not line.startswith("#")]
    
    # Ensure standard exclusions exist
    assert ".git" in lines
    assert ".venv" in lines
    assert "__pycache__/" in lines or "__pycache__" in lines

    # Issue 4: Build-context secrets and output exclusions
    assert ".env" in lines, ".dockerignore must exclude .env"
    assert ".env.*" in lines, ".dockerignore must exclude .env.*"
    assert "!.env.example" in lines, ".dockerignore must explicitly keep/include .env.example"
    assert "outputs/" in lines or "outputs" in lines, ".dockerignore must exclude outputs/ directory"
    
    # Verify we do NOT exclude required RAG or SKILL docs
    docs_to_keep = ["README.md", "PROJECT_CONTEXT.md", "walkthrough.md", "SKILL.md", "docs/", "data/"]
    for doc in docs_to_keep:
        assert doc not in lines, f".dockerignore should not block {doc}"
        assert f"/{doc}" not in lines
        assert f"./{doc}" not in lines

def test_env_example_exists_and_valid():
    env_example_path = ".env.example"
    assert os.path.exists(env_example_path), ".env.example must exist at the root"
    
    with open(env_example_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    assert "PORT=8080" in content
    assert "BOC_ENV=production" in content
    assert "BOC_SKILL_FILE_PATH=SKILL.md" in content
    
    # Ensure no fake secrets or credentials exist
    for line in content.splitlines():
        if "=" in line:
            parts = line.split("=", 1)
            val = parts[1].strip()
            # Ensure no dummy/placeholder secret values
            assert not any(x in val.lower() for x in ["dummy", "fake", "placeholder_key", "sk-", "aiza"]), \
                f"Fake or placeholder secret detected in .env.example: {line}"

def test_deployment_guide_exists_and_valid():
    guide_path = "docs/deployment_cloud_run.md"
    assert os.path.exists(guide_path), "deployment_cloud_run.md must exist in docs/"
    
    with open(guide_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Asserts safe instances configuration
    assert "min-instances 0" in content.lower() or "min instances: 0" in content.lower() or "min_instances 0" in content.lower()
    assert "max-instances 1" in content.lower() or "max instances: 1" in content.lower() or "max_instances 1" in content.lower()
    
    # Issue 3: Cost shutdown/cost command checks
    assert "--max-instances 0" not in content, "Do not recommend --max-instances 0 for Cloud Run shutdown"
    assert "guarantee zero active billing" not in content.lower(), "Do not promise guaranteed zero active billing"
    assert "gcloud run services delete" in content, "Definitive shutdown should recommend deleting the Cloud Run service"
    assert "--no-allow-unauthenticated" in content, "Private authenticated deployment must be the documented default"

    # Cloud Run IAM role assertions (Issue 1)
    assert "roles/run.sourceDeveloper" in content
    assert "roles/serviceusage.serviceUsageConsumer" in content
    assert "roles/run.builder" in content
    assert "roles/iam.serviceAccountUser" in content
    assert "roles/run.invoker" in content
    assert "add-iam-policy-binding" in content
    assert "--build-service-account" in content
    assert "cloudbuild.gserviceaccount.com" in content
    assert "developer.gserviceaccount.com" in content

    # Private deployment smoke testing assertions (Issue 2)
    assert "gcloud run services proxy" in content.lower()
    assert "print-identity-token" in content.lower()

    # Deletion cost disclaimer assertions (Issue 3)
    assert "other related resources" in content.lower() or "may still incur costs" in content.lower()
    assert "fully eliminate all billing" not in content.lower()

    # Verify no Vertex/Gemini in Phase 10.1
    assert "vertex" in content.lower()
    assert "gemini" in content.lower()
    
    # Verify budget/cost guardrails references for Phase 10.2
    assert "phase 10.2" in content.lower() or "cost control" in content.lower() or "budget" in content.lower()

def test_no_local_absolute_paths_in_docs():
    # Issue 5: Search for absolute local paths in documentation files
    docs_dir = "docs"
    markdown_files = [os.path.join(docs_dir, f) for f in os.listdir(docs_dir) if f.endswith(".md")]
    markdown_files.extend(["README.md", "PROJECT_CONTEXT.md", "walkthrough.md", "SKILL.md"])
    
    forbidden_patterns = ["file:///f:", "file:///F:", "file:///c:", "file:///C:", "f:/studyspace", "F:/studyspace"]
    
    for file_path in markdown_files:
        if not os.path.exists(file_path):
            continue
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read().lower()
        for pattern in forbidden_patterns:
            assert pattern not in content, f"Absolute local path pattern '{pattern}' detected in {file_path}"

def test_smoke_script_execution():
    # Verify smoke script runs cleanly without raising SystemExit or errors
    try:
        smoke_main()
    except SystemExit as e:
        assert e.code == 0, f"Smoke script exited with non-zero code: {e.code}"

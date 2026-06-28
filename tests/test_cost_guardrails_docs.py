import os
import pytest

def test_cost_guardrails_guide_exists_and_valid():
    guide_path = "docs/cost_guardrails.md"
    assert os.path.exists(guide_path), "cost_guardrails.md must exist in docs/"
    
    with open(guide_path, "r", encoding="utf-8") as f:
        content = f.read()
        lower_content = content.lower()
    
    # 2. Mentions --min-instances 0
    assert "--min-instances 0" in content or "min-instances 0" in content or "min instances: 0" in content.lower()
    
    # 3. Mentions --max-instances 1
    assert "--max-instances 1" in content or "max-instances 1" in content or "max instances: 1" in content.lower()
    
    # 4. Mentions budget alerts
    assert "budget alerts" in lower_content or "alert thresholds" in lower_content
    
    # 5. Cautious language about budget alerts (not hard caps, not guarantees)
    # Require explicit negation strings (Issue 2.1)
    assert "not a hard spending cap" in lower_content
    assert "not hard caps" in lower_content
    assert "not a guarantee" in lower_content or "not guarantee" in lower_content
    
    # Budget alerts negative checks (Issue 2.2)
    assert "budget alerts stop billing" not in lower_content
    assert "budget alerts stop all billing" not in lower_content
    assert "alerts stop billing" not in lower_content
    assert "alerts do not stop billing" in lower_content or "do not shut down billing" in lower_content
    
    # 6. Does not say "free deployment"
    assert "free deployment" not in lower_content
    
    # 7. Does not say "zero cost guaranteed"
    assert "zero cost guaranteed" not in lower_content
    
    # 9. Mentions deleting Cloud Run service
    assert "gcloud run services delete" in lower_content
    
    # 10. Mentions Artifact Registry or build artifacts may still incur costs
    assert "artifact registry" in lower_content
    assert "incur charges" in lower_content or "incur costs" in lower_content or "incur fees" in lower_content
    
    # Independent cost cautions assertions (Issue 2.4)
    assert "artifact registry" in lower_content
    assert "cloud build" in lower_content
    assert "cloud logging" in lower_content
    assert "storage" in lower_content
    
    # Cautious max instances language (Issue 2.5)
    assert "guardrail" in lower_content
    assert "not a hard guarantee" in lower_content or "no hard guarantee" in lower_content
    
    # 11. Mentions private deployment by default
    assert "private default" in lower_content or "private by default" in lower_content or "private deployment" in lower_content
    
    # 12. Mentions synthetic workbook / no sensitive production data
    assert "synthetic" in lower_content
    assert "sensitive" in lower_content
    
    # 13. Says no Vertex/Gemini in Phase 10.2 (Issue 2.3)
    assert "does not deploy vertex" in lower_content
    assert "does not deploy gemini" in lower_content
    
    # 14. References Phase 10.3 as optional ADK/Vertex migration guide
    assert "phase 10.3" in lower_content
    assert "migration" in lower_content

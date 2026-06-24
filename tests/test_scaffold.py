import pytest

def test_imports():
    """Verifies that all packaged modules can be imported correctly without syntax errors."""
    try:
        import boc_agent
        from boc_agent.schemas.transaction import TransactionRecord, Transaction
        from boc_agent.schemas.review_result import ReviewResult
        from boc_agent.io.workbook_loader import load_workbook
        from boc_agent.io.workbook_exporter import export_reviewed_workbook
        from boc_agent.tools.allocation_tool import review_transaction
        from boc_agent.rules.allocation_rules import ALLOCATION_COLUMNS
        from boc_agent.agents.orchestrator import Orchestrator
        from boc_agent.cli import main
    except ImportError as e:
        pytest.fail(f"Scaffold import verification failed: {e}")
        
def test_boc_agent_version():
    """Verifies version definition in the root package."""
    import boc_agent
    assert hasattr(boc_agent, "__version__")
    assert boc_agent.__version__ == "0.1.0"

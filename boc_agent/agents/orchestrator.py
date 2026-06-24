from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from boc_agent.schemas.transaction import TransactionRecord
from boc_agent.schemas.review_result import ReviewResult
from boc_agent.tools.security_guardrail_tool import scan_prompt_injection
from boc_agent.tools.classification_tool import classify_transaction
from boc_agent.tools.eligibility_tool import evaluate_eligibility
from boc_agent.tools.allocation_wrapper_tool import suggest_allocation
from boc_agent.tools.review_tool import make_review_decision

@dataclass
class OrchestrationState:
    """Represents the execution state of a transaction review through the agent pipeline."""
    transaction: TransactionRecord
    security_flags: List[str] = field(default_factory=list)
    classification: Dict[str, Any] = field(default_factory=dict)
    deterministic_result: Optional[ReviewResult] = None
    final_result: Optional[ReviewResult] = None
    trace: List[str] = field(default_factory=list)

class Orchestrator:
    """Orchestrates the local-first execution flow for GL transaction review.
    
    Coordinates the wrapper tools (security, classification, eligibility, allocation, review)
    in a structured agent-like pipeline.
    """
    
    def orchestrate_transaction_review(self, tx: TransactionRecord) -> ReviewResult:
        """Runs the sequential orchestration pipeline for a single transaction."""
        state = OrchestrationState(transaction=tx)
        
        # 1. Security Guardrail Check
        state.trace.append("Step 1: Security guardrail scan started.")
        state.security_flags = scan_prompt_injection(tx)
        state.trace.append(f"Step 1 finished. Security warnings: {len(state.security_flags)}")
        
        # 2. Transaction Classification
        state.trace.append("Step 2: Transaction classification started.")
        state.classification = classify_transaction(tx)
        state.trace.append("Step 2 finished.")
        
        # 3. Eligibility Assessment
        state.trace.append("Step 3: Eligibility evaluation started.")
        # Evaluate eligibility (reads deterministic outcome safely)
        eligibility = evaluate_eligibility(tx)
        state.trace.append(f"Step 3 finished. Status: {eligibility.get('eligibility_status')}")
        
        # 4. Allocation Suggestion
        state.trace.append("Step 4: Deterministic allocation suggestion started.")
        state.deterministic_result = suggest_allocation(tx)
        state.trace.append("Step 4 finished.")
        
        # 5. Final Review Packaging
        state.trace.append("Step 5: Review result packaging started.")
        state.final_result = make_review_decision(
            tx=tx,
            classification_metadata=state.classification,
            security_warnings=state.security_flags,
            allocation_result=state.deterministic_result
        )
        state.trace.append("Step 5 finished.")
        
        return state.final_result
        
    def orchestrate_batch_review(self, transactions: List[TransactionRecord]) -> List[ReviewResult]:
        """Executes transaction reviews in a batch loop."""
        results = []
        for tx in transactions:
            results.append(self.orchestrate_transaction_review(tx))
        return results
        
    def process_transaction(self, tx: TransactionRecord) -> ReviewResult:
        """Maintains the backward-compatible entry point for the CLI."""
        return self.orchestrate_transaction_review(tx)


from pydantic import BaseModel, Field
from typing import Optional, Literal

class HumanReviewDecision(BaseModel):
    """Pydantic model representing a human reviewer's decision for audit purposes."""
    transaction_ref: str = Field(..., description="Reference transaction identifier")
    reviewer_decision: Literal[
        "Accept Agent Suggestion",
        "Override Allocation",
        "Mark Ineligible",
        "Request More Documentation",
        "Defer"
    ] = Field(..., description="Decision status: Accept Agent Suggestion, Override Allocation, Mark Ineligible, Request More Documentation, Defer")
    reviewer_comment: str = Field(..., description="Comment or justification for decision")
    reviewer_name: Optional[str] = Field(None, description="Name of the human auditor")
    reviewed_at: str = Field(..., description="Review timestamp")
    override_allocation: Optional[str] = Field(None, description="Provincial/Federal override target bucket")
    override_reason: Optional[str] = Field(None, description="Reason for override")

def apply_human_decision(row_dict: dict, decision: HumanReviewDecision) -> dict:
    """Appends human review metadata to a transaction row dictionary, preserving all original fields."""
    updated = row_dict.copy()
    updated["human_review_decision"] = decision.reviewer_decision
    updated["human_review_comment"] = decision.reviewer_comment
    updated["human_reviewer"] = decision.reviewer_name
    updated["human_reviewed_at"] = decision.reviewed_at
    updated["human_override_allocation"] = decision.override_allocation
    updated["human_override_reason"] = decision.override_reason
    return updated

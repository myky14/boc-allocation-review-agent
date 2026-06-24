from pydantic import BaseModel, Field
from typing import Optional

class ReviewResult(BaseModel):
    """Pydantic schema representing the output columns added to the general ledger after review."""
    suggested_allocation_column: str = Field(..., description="Suggested tax-credit allocation column (bucket)")
    amount_percentage: float = Field(100.0, description="Suggested allocation claim percentage (e.g. 100.0 or 65.0)")
    eligibility_status: str = Field(..., description="Suggested eligibility status (e.g. Eligible, Ineligible)")
    confidence_score: float = Field(1.0, description="Confidence score between 0.0 and 1.0")
    review_status: str = Field(..., description="Review recommendation (e.g. Approved, Needs Human Review)")
    rationale: str = Field(..., description="Logic explanation for suggestions")
    reference_rule: str = Field(..., description="Specific reference rule applied")
    secondary_allocation_note: Optional[str] = Field(None, description="Detailed splits or notes for remaining amounts")

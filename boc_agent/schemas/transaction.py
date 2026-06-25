import pandas as pd
from pydantic import BaseModel, Field, ConfigDict, PrivateAttr
from typing import Optional

class TransactionRecord(BaseModel):
    """Pydantic model representing a raw synthetic GL transaction record from the workbook."""
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
        extra="allow"
    )

    _original_keys: list[str] = PrivateAttr(default_factory=list)

    account: str = Field(..., alias="Account")
    account_name: str = Field(..., alias="Account Name")
    trans_date: str = Field(..., alias="Trans Date")
    src: Optional[str] = Field(None, alias="Src")
    trans_ref: Optional[str] = Field(None, alias="Trans Ref")
    vendor_id: Optional[str] = Field(None, alias="Vendor ID")
    vendor_name: Optional[str] = Field(None, alias="Vendor Name")
    description: Optional[str] = Field(None, alias="Description")
    additional_description: Optional[str] = Field(None, alias="Additional Description")
    loan_out_corp: Optional[str] = Field(None, alias="Loan out corp")
    employee: Optional[str] = Field(None, alias="Employee")
    tax_id: Optional[str] = Field(None, alias="Tax ID")
    address: Optional[str] = Field(None, alias="Address")
    city: Optional[str] = Field(None, alias="City")
    province: Optional[str] = Field(None, alias="Province")
    country: Optional[str] = Field(None, alias="Country")
    zip_code: Optional[str] = Field(None, alias="Zip Code")
    our_reference: Optional[str] = Field(None, alias="Our Reference")
    currency: Optional[str] = Field(None, alias="Currency")
    usd: Optional[float] = Field(None, alias="USD")
    application_province: Optional[str] = Field(None, alias="Application Province")
    location: Optional[str] = Field(None, alias="Location")
    ep: Optional[str] = Field(None, alias="Ep")
    amount: float = Field(..., alias="Amount")

    @classmethod
    def from_row_dict(cls, row_dict: dict) -> "TransactionRecord":
        """Creates a TransactionRecord from a dictionary, safely handling NaN/null values from pandas."""
        cleaned = {}
        for k, v in row_dict.items():
            if pd.isna(v) or v is None:
                cleaned[k] = None
            else:
                # Convert float representations of integers or IDs to clean strings if they end with .0
                if isinstance(v, float) and v.is_integer() and k not in ["USD", "Amount"]:
                    cleaned[k] = str(int(v))
                else:
                    cleaned[k] = str(v) if k not in ["USD", "Amount"] else v
        instance = cls.model_validate(cleaned)
        instance._original_keys = list(row_dict.keys())
        return instance

# Keep Transaction as an alias to TransactionRecord to maintain package consistency
Transaction = TransactionRecord

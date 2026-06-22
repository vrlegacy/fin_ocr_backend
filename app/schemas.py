from pydantic import BaseModel, ConfigDict, field_validator
from typing import Optional, List
from datetime import datetime

def format_amount_rupees(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    s = str(v).strip()
    if not s or s.lower() in ("null", "none"):
        return s
    if s.startswith("₹"):
        return s
    if s.startswith("-"):
        val = s[1:].strip()
        if val.startswith("₹"):
            return s
        return f"-₹{val}"
    return f"₹{s}"

# --- User Schemas ---
class UserBase(BaseModel):
    email: str
    username: Optional[str] = None
    role: Optional[str] = None

class UserCreate(UserBase):
    auth0_sub: str

class UserResponse(UserBase):
    id: int
    auth0_user_id: str  # maps to auth0_sub for frontend compatibility
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- Expense Schemas ---
class ExpenseBase(BaseModel):
    merchant_name: Optional[str] = None
    transaction_date: Optional[str] = None
    invoice_number: Optional[str] = None
    category: Optional[str] = None
    payment_method: Optional[str] = None
    tax_id: Optional[str] = None
    notes: Optional[str] = None
    items_list: Optional[str] = None
    subtotal: Optional[str] = None
    tax_amount: Optional[str] = None
    total_amount: Optional[str] = None
    discount: Optional[str] = None
    card_ending: Optional[str] = None
    status: Optional[str] = "Verified"

    @field_validator('subtotal', 'tax_amount', 'total_amount', 'discount')
    @classmethod
    def format_amount_fields(cls, v: Optional[str]) -> Optional[str]:
        return format_amount_rupees(v)

class ExpenseCreate(ExpenseBase):
    pass

class ExpenseUpdate(BaseModel):
    merchant_name: Optional[str] = None
    transaction_date: Optional[str] = None
    invoice_number: Optional[str] = None
    category: Optional[str] = None
    payment_method: Optional[str] = None
    tax_id: Optional[str] = None
    notes: Optional[str] = None
    items_list: Optional[str] = None
    subtotal: Optional[str] = None
    tax_amount: Optional[str] = None
    total_amount: Optional[str] = None
    discount: Optional[str] = None
    card_ending: Optional[str] = None
    status: Optional[str] = None

    @field_validator('subtotal', 'tax_amount', 'total_amount', 'discount')
    @classmethod
    def format_amount_fields(cls, v: Optional[str]) -> Optional[str]:
        return format_amount_rupees(v)

class ExpenseResponse(ExpenseBase):
    id: int
    user_id: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)

# --- OCR Scanned Bill Schema ---
# Standard structured schema returned by Gemini OCR API
class OcrResponse(BaseModel):
    merchantName: str
    transactionDate: str
    invoiceNumber: str
    category: str
    paymentMethod: str
    taxId: str
    notes: str
    itemsList: str
    subtotal: str
    taxAmount: str
    totalAmount: str
    discount: str
    cardEnding: str

    @field_validator('subtotal', 'taxAmount', 'totalAmount', 'discount')
    @classmethod
    def format_amount_fields(cls, v: Optional[str]) -> Optional[str]:
        return format_amount_rupees(v)

from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime
from uuid import UUID
from decimal import Decimal

class UserBase(BaseModel):
    email: EmailStr
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class PurchaseOrderResponse(BaseModel):
    id: UUID
    company_name: Optional[str]
    vendor_name: Optional[str]
    credit_days: Optional[int]
    order_tracking: Optional[str]
    total_amount: Decimal
    gst_amount: Decimal
    base_amount: Decimal
    four_percent_amount: Decimal
    status: str
    uploaded_at: datetime

    class Config:
        from_attributes = True

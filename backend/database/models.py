import uuid
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey, Numeric, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from .db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    company_name = Column(String(255))
    first_name = Column(String(100))
    last_name = Column(String(100))
    role = Column(String(50), default="user") # 'admin' or 'user'
    is_active = Column(Boolean, default=True)
    reset_code = Column(String(10), nullable=True)
    reset_code_expires = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class Vendor(Base):
    __tablename__ = "vendors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    vendor_name = Column(String(255), nullable=False)
    email = Column(String(255))
    phone = Column(String(20))
    address = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class PurchaseOrder(Base):
    __tablename__ = "purchase_orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    company_name = Column(String(255))
    vendor_name = Column(String(255))
    credit_days = Column(Integer)
    order_tracking = Column(String(100))
    
    total_amount = Column(Numeric(12, 2))
    gst_amount = Column(Numeric(12, 2))
    base_amount = Column(Numeric(12, 2))
    four_percent_amount = Column(Numeric(12, 2))
    
    ordered_quantity = Column(Integer, default=0)
    
    file_path = Column(String(500))
    file_type = Column(String(50))
    status = Column(String(50), default="PROCESSING") # PROCESSING, COMPLETED, FAILED
    
    uploaded_by = Column(String(255))
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())

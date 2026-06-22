from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    auth0_sub = Column(String, unique=True, index=True, nullable=True)
    username = Column(String, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    role = Column(String, nullable=True)  # Financial Persona
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    expenses = relationship("Expense", back_populates="user", cascade="all, delete-orphan")

class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Bill & Vendor Details
    merchant_name = Column(String, nullable=True)
    transaction_date = Column(String, nullable=True)
    invoice_number = Column(String, nullable=True)
    category = Column(String, nullable=True)
    payment_method = Column(String, nullable=True)
    tax_id = Column(String, nullable=True)
    notes = Column(Text, nullable=True)

    # Line Items & Amounts
    items_list = Column(Text, nullable=True)
    subtotal = Column(String, nullable=True)
    tax_amount = Column(String, nullable=True)
    total_amount = Column(String, nullable=True)
    discount = Column(String, nullable=True)
    card_ending = Column(String, nullable=True)

    # Audit & Status
    status = Column(String, default="Verified")  # e.g., "Verified", "Needs Review"
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="expenses")

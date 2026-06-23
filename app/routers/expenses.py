from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, Expense
from app.schemas import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from app.auth import get_current_user

router = APIRouter(prefix="/api/expenses", tags=["Expenses"])

@router.get("", response_model=List[ExpenseResponse])
def get_expenses(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Fetch all expenses belonging to current user, ordered by uploaded time desc
    return db.query(Expense).filter(Expense.user_id == current_user.id).order_by(Expense.uploaded_at.desc()).all()

@router.post("", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
def create_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_expense = Expense(
        **expense_data.model_dump(),
        user_id=current_user.id
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

@router.get("/{expense_id}", response_model=ExpenseResponse)
def get_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense record not found"
        )
    return expense

@router.put("/{expense_id}", response_model=ExpenseResponse)
def update_expense(
    expense_id: int,
    expense_data: ExpenseUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense record not found"
        )
    
    update_dict = expense_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(expense, key, value)
        
    db.commit()
    db.refresh(expense)
    return expense

@router.delete("/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expense = db.query(Expense).filter(Expense.id == expense_id, Expense.user_id == current_user.id).first()
    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Expense record not found"
        )
    
    db.delete(expense)
    db.commit()
    return None

import re
from collections import defaultdict
from app.services.gemini import generate_insights_with_gemini

# Color mapping helper for frontend categories
COLOR_MAP = {
    "Food": "bg-emerald-500",
    "Shopping": "bg-blue-500",
    "Travel": "bg-indigo-500",
    "Bills": "bg-amber-500",
    "Electronics": "bg-purple-500",
    "Others": "bg-slate-400"
}

def parse_amount(val_str: str) -> float:
    if not val_str:
        return 0.0
    clean = re.sub(r"[^\d.]", "", val_str)
    try:
        return float(clean) if clean else 0.0
    except ValueError:
        return 0.0

@router.get("/analysis/categories")
def get_categories_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expenses = db.query(Expense).filter(Expense.user_id == current_user.id).all()
    
    category_totals = defaultdict(float)
    category_counts = defaultdict(int)
    total_spend = 0.0
    
    for exp in expenses:
        cat = exp.category or "Others"
        amount = parse_amount(exp.total_amount)
        category_totals[cat] += amount
        category_counts[cat] += 1
        total_spend += amount
        
    results = []
    for cat, amount in category_totals.items():
        pct = int((amount / total_spend * 100)) if total_spend > 0 else 0
        results.append({
            "name": cat,
            "amount": f"₹{amount:,.2f}",
            "numeric_amount": amount,
            "percent": pct,
            "color": COLOR_MAP.get(cat, "bg-slate-400"),
            "count": category_counts[cat]
        })
        
    results.sort(key=lambda x: x["numeric_amount"], reverse=True)
    return results

@router.get("/analysis/insights")
def get_insights_analysis(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    expenses = db.query(Expense).filter(Expense.user_id == current_user.id).all()
    
    category_totals = defaultdict(float)
    total_spend = 0.0
    
    for exp in expenses:
        cat = exp.category or "Others"
        amount = parse_amount(exp.total_amount)
        category_totals[cat] += amount
        total_spend += amount
        
    top_cat = "None"
    top_cat_amt = 0.0
    if category_totals:
        top_cat = max(category_totals, key=category_totals.get)
        top_cat_amt = category_totals[top_cat]
        
    categories_summary = {cat: f"₹{amt:.2f}" for cat, amt in category_totals.items()}
    
    summary = {
        "total_spent": total_spend,
        "count": len(expenses),
        "categories": categories_summary,
        "top_category": top_cat,
        "top_category_amount": top_cat_amt
    }
    
    insights = generate_insights_with_gemini(summary)
    return insights


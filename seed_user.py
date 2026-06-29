import os
import sys

# Ensure backend directory is in the path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app.database import SessionLocal
from app.models import User, Expense

def seed():
    db = SessionLocal()
    try:
        # Check if user already exists
        user = db.query(User).filter(User.email == "testuser@mail.com").first()
        if not user:
            user = User(
                auth0_sub="auth0|local_testuser_mail.com",
                username="testuser",
                email="testuser@mail.com"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created user: {user.username} (ID: {user.id})")
        else:
            print(f"User already exists: {user.username} (ID: {user.id})")

        # Now check if this user has expenses, if not add some demo ones
        existing_expenses = db.query(Expense).filter(Expense.user_id == user.id).count()
        if existing_expenses == 0:
            demo_expenses = [
                Expense(
                    user_id=user.id,
                    merchant_name="Starbucks",
                    transaction_date="2026-06-20",
                    invoice_number="INV-2026-001",
                    category="Food",
                    payment_method="Credit Card",
                    tax_id="GST-123456",
                    notes="Morning coffee and croissant",
                    items_list="1x Latte (₹250), 1x Croissant (₹150)",
                    subtotal="₹400",
                    tax_amount="₹20",
                    total_amount="₹420",
                    discount="₹0",
                    card_ending="1234",
                    status="Verified"
                ),
                Expense(
                    user_id=user.id,
                    merchant_name="Amazon India",
                    transaction_date="2026-06-21",
                    invoice_number="INV-2026-002",
                    category="Shopping",
                    payment_method="UPI",
                    tax_id="GST-789012",
                    notes="Noise cancelling headphones",
                    items_list="1x Headphones (₹4500)",
                    subtotal="₹4500",
                    tax_amount="₹810",
                    total_amount="₹5310",
                    discount="₹200",
                    card_ending="",
                    status="Verified"
                ),
                Expense(
                    user_id=user.id,
                    merchant_name="Uber",
                    transaction_date="2026-06-22",
                    invoice_number="INV-2026-003",
                    category="Travel",
                    payment_method="Credit Card",
                    tax_id="",
                    notes="Ride to office",
                    items_list="1x Uber Go ride (₹350)",
                    subtotal="₹350",
                    tax_amount="₹18",
                    total_amount="₹368",
                    discount="₹0",
                    card_ending="1234",
                    status="Verified"
                ),
                Expense(
                    user_id=user.id,
                    merchant_name="Netflix",
                    transaction_date="2026-06-15",
                    invoice_number="INV-2026-004",
                    category="Bills",
                    payment_method="Auto-debit",
                    tax_id="",
                    notes="Monthly premium subscription",
                    items_list="1x Netflix Premium (₹649)",
                    subtotal="₹649",
                    tax_amount="₹0",
                    total_amount="₹649",
                    discount="₹0",
                    card_ending="5678",
                    status="Verified"
                ),
                Expense(
                    user_id=user.id,
                    merchant_name="Croma Electronics",
                    transaction_date="2026-06-18",
                    invoice_number="INV-2026-005",
                    category="Electronics",
                    payment_method="Debit Card",
                    tax_id="GST-445566",
                    notes="Office monitor",
                    items_list="1x 27-inch IPS Monitor (₹15000)",
                    subtotal="₹15000",
                    tax_amount="₹2700",
                    total_amount="₹17700",
                    discount="₹1000",
                    card_ending="9012",
                    status="Verified"
                )
            ]
            db.bulk_save_objects(demo_expenses)
            db.commit()
            print(f"Successfully pushed 5 demo transactions for user {user.email}.")
        else:
            print(f"User already has {existing_expenses} transactions. Skipping demo transactions push.")

    except Exception as e:
        db.rollback()
        print(f"Error seeding user: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed()

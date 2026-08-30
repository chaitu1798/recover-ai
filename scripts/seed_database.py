import os
import sys
import uuid
import json

# Add backend directory to sys.path so we can import app modules
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(backend_path)

from app.database import SessionLocal, engine, Base
from app.models import Merchant, Customer, Policy, enums

def seed_database():
    print("Seeding database...")
    db = SessionLocal()
    
    try:
        # Create a single demo merchant
        merchant = db.query(Merchant).filter(Merchant.name == "Demo Merchant").first()
        if not merchant:
            merchant = Merchant(
                id=uuid.uuid4(),
                name="Demo Merchant",
                razorpay_account_id="acc_demo123",
                environment="test",
                currency="INR"
            )
            db.add(merchant)
            db.commit()
            db.refresh(merchant)
            print(f"Created merchant: {merchant.name} (ID: {merchant.id})")
        else:
            print(f"Merchant {merchant.name} already exists (ID: {merchant.id})")
            
        # Create a default policy
        policy = db.query(Policy).filter(Policy.merchant_id == merchant.id).first()
        if not policy:
            policy = Policy(
                id=uuid.uuid4(),
                merchant_id=merchant.id,
                policy_name="Default Recovery Policy",
                max_attempts=2,
                min_confidence=0.80,
                max_auto_action_amount=1000000, # 10,000 INR
                enabled=True,
                rules={"rule": "default"}
            )
            db.add(policy)
            db.commit()
            print("Created default recovery policy")
        else:
            print("Default policy already exists")
            
        # Create a few demo customers manually if needed, 
        # but the synthetic data import script handles creating customers.
            
        print("Database seeding completed.")
    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()

import csv
import sys
import os
import uuid
from datetime import datetime

backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(backend_path)

from app.database import SessionLocal
from app.models import Merchant, Customer, Order, Payment, PaymentEvent, RecoveryCase

def import_synthetic_data():
    db = SessionLocal()
    
    try:
        merchant = db.query(Merchant).filter(Merchant.name == "Demo Merchant").first()
        if not merchant:
            print("Merchant not found. Run seed_database.py first.")
            return

        with open("data/synthetic/payments.csv", "r", encoding="utf-8") as f:
            records = list(csv.DictReader(f))
            
        print(f"Importing {len(records)} records...")
        
        # We will create objects in memory to bulk save if possible, 
        # but a simple loop works fine for 2000 records.
        
        for row in records:
            # Check customer
            ext_cust_id = row["customer_id"]
            customer = db.query(Customer).filter(
                Customer.merchant_id == merchant.id,
                Customer.external_customer_id == ext_cust_id
            ).first()
            
            if not customer:
                customer = Customer(
                    id=uuid.UUID(ext_cust_id),
                    merchant_id=merchant.id,
                    external_customer_id=ext_cust_id,
                    name=f"Customer {ext_cust_id[:8]}",
                    total_orders=1,
                    failed_orders=1,
                    total_spend=int(row["amount"])
                )
                db.add(customer)
                db.commit() # commit needed to reference
                
            # Check if Payment already exists (Idempotency)
            payment_id = uuid.UUID(row["payment_id"])
            existing_payment = db.query(Payment).filter(Payment.id == payment_id).first()
            if existing_payment:
                continue # Skip importing this record if it already exists

            # Create Order
            order = Order(
                id=uuid.uuid4(),
                merchant_id=merchant.id,
                customer_id=customer.id,
                razorpay_order_id=f"order_{uuid.uuid4().hex[:14]}",
                amount=int(row["amount"]),
                currency=row["currency"],
                status="attempted",
                created_at=datetime.fromisoformat(row["created_at"])
            )
            db.add(order)
            db.commit()
            
            # Create Payment
            payment = Payment(
                id=payment_id,
                merchant_id=merchant.id,
                customer_id=customer.id,
                order_id=order.id,
                razorpay_payment_id=f"pay_{uuid.uuid4().hex[:14]}",
                amount=int(row["amount"]),
                currency=row["currency"],
                method=row["payment_method"],
                status=row["payment_status"],
                error_description=row["failure_reason"],
                attempt_number=int(row["attempt_number"]),
                failed_at=datetime.fromisoformat(row["created_at"]),
                created_at=datetime.fromisoformat(row["created_at"])
            )
            db.add(payment)
            db.commit()
            
            # Create Payment Event
            event = PaymentEvent(
                id=uuid.uuid4(),
                payment_id=payment.id,
                event_type="payment.failed",
                razorpay_event_id=f"evt_{uuid.uuid4().hex[:14]}",
                payload={"simulated": True, "reason": row["failure_reason"]},
                received_at=datetime.fromisoformat(row["created_at"]),
                processing_status="processed"
            )
            db.add(event)
            
            # Create Recovery Case if eligible (deterministic Phase 2 rules: e.g. amount > 0 and recoverable status)
            if int(row["amount"]) > 0:
                rc = RecoveryCase(
                    id=uuid.uuid4(),
                    payment_id=payment.id,
                    status="open",
                    amount_at_risk=int(row["amount"]),
                    priority_score=int(row["amount"]) * 0.001, # simple priority
                    eligible=True,
                    eligibility_reason="Deterministic eligibility",
                    opened_at=datetime.fromisoformat(row["created_at"])
                )
                db.add(rc)
                
            db.commit()
            
        print("Import complete.")
        
    except Exception as e:
        print(f"Error importing data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import_synthetic_data()

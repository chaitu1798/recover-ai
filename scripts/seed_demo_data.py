"""
RecoverAI Deterministic Buildathon Demo Data Seeder

SAFETY CONTROLS:
- Operates ONLY when ENVIRONMENT is in ['test', 'development', 'local']
- Operates ONLY when RAZORPAY_MODE == 'test'
- Refuses to run against production database URLs
- Never calls live financial APIs (no real money moved)
- Completely repeatable and idempotent
"""

import os
import sys
import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import text
from sqlalchemy.orm import Session

# Add backend directory to sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend'))
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.config import settings  # type: ignore
from app.database import SessionLocal, engine  # type: ignore
from app.models import (  # type: ignore
    Merchant,
    Customer,
    Order,
    Payment,
    PaymentEvent,
    RecoveryCase,
    RecoveryDecision,
    RecoveryActionModel,
    ActionResult,
    Policy,
    AuditLog
)
from app.models.enums import ApprovalStatus  # type: ignore
from app.agent.recovery_agent import analyze_recovery_case  # type: ignore
from app.recovery.state_machine import (  # type: ignore
    transition_to_approved,
    transition_to_rejected,
    transition_to_executing,
    transition_to_recovered,
    transition_to_failed
)

def assert_demo_safety():
    """Ensure we never run against production or live mode."""
    if getattr(settings, "RAZORPAY_MODE", "") != "test":
        raise RuntimeError(f"SAFETY VIOLATION: Cannot seed demo data in RAZORPAY_MODE='{getattr(settings, 'RAZORPAY_MODE', '')}'")
        
    db_url = str(settings.DATABASE_URL).lower()
    if "prod" in db_url or "live" in db_url:
        raise RuntimeError("SAFETY VIOLATION: Production database URL detected")

def reset_database(db: Session):
    """Safely reset test tables for clean demo state."""
    print("Safely resetting local demo database tables...")
    truncate_sql = text("""
        TRUNCATE TABLE 
            audit_logs,
            action_results,
            recovery_actions,
            recovery_decisions,
            experiment_assignments,
            recovery_cases,
            payment_events,
            payments,
            orders,
            customers,
            policies,
            merchants
        CASCADE;
    """)
    db.execute(truncate_sql)
    db.commit()
    print("Database reset complete.")

def seed_demo_dataset():
    """Generates a clean, deterministic 20-case dataset for the Buildathon demonstration."""
    assert_demo_safety()
    db = SessionLocal()

    try:
        reset_database(db)

        # 1. Create Demo Merchant
        merchant = Merchant(
            id=uuid.uuid4(),
            name="Acme Retail India (Demo Merchant)",
            razorpay_account_id="acc_demo_acme_retail",
            environment="test",
            currency="INR"
        )
        db.add(merchant)
        db.commit()
        db.refresh(merchant)
        print(f"Created Merchant: {merchant.name} (ID: {merchant.id})")

        # 2. Create Merchant Policy
        policy = Policy(
            id=uuid.uuid4(),
            merchant_id=merchant.id,
            policy_name="Standard Recovery Policy",
            max_attempts=2,
            min_confidence=0.30,
            max_auto_action_amount=10000000, # INR 100,000.00
            enabled=True,
            rules={
                "rule": "default",
                "unsupported_failures": ["FRAUD_SUSPECTED"]
            }
        )
        db.add(policy)
        db.commit()
        print("Created Default Recovery Policy")

        # 3. Create Customers
        customers_def = [
            ("Rahul Sharma", "rahul.sharma@example.com", "+919876543210"),
            ("Priya Patel", "priya.patel@example.com", "+919876543211"),
            ("Vikram Singh", "vikram.singh@example.com", "+919876543212"),
            ("Sunita Rao", "sunita.rao@example.com", "+919876543213"),
            ("Ananya Iyer", "ananya.iyer@example.com", "+919876543214"),
            ("Rajesh Kumar", "rajesh.kumar@example.com", "+919876543215"),
            ("Amit Verma", "amit.verma@example.com", "+919876543216"),
            ("Sneha Reddy", "sneha.reddy@example.com", "+919876543217"),
            ("Karan Mehta", "karan.mehta@example.com", "+919876543218"),
            ("Divya Nair", "divya.nair@example.com", "+919876543219"),
            ("Arjun Kapoor", "arjun.kapoor@example.com", "+919876543220"),
            ("Neha Gupta", "neha.gupta@example.com", "+919876543221"),
            ("Siddharth Joshi", "siddharth.joshi@example.com", "+919876543222"),
            ("Manoj Tiwari", "manoj.tiwari@example.com", "+919876543223"),
            ("Pooja Hegde", "pooja.hegde@example.com", "+919876543224"),
            ("Rohan Das", "rohan.das@example.com", "+919876543225"),
            ("Kavita Menon", "kavita.menon@example.com", "+919876543226"),
            ("Deepak Chawla", "deepak.chawla@example.com", "+919876543227"),
            ("Security Review User", "security.review@example.com", "+919876543228"),
            ("Guest Checkout", "guest.checkout@example.com", "+919876543229"),
        ]

        customer_objs = []
        for name, email, phone in customers_def:
            cust = Customer(
                id=uuid.uuid4(),
                merchant_id=merchant.id,
                name=name,
                email=email,
                phone=phone,
                total_orders=1,
                failed_orders=1,
                total_spend=0
            )
            db.add(cust)
            customer_objs.append(cust)
        db.commit()

        # 4. Specification for 20 Deterministic Demo Recovery Cases
        now = datetime.now(timezone.utc)
        cases_spec = [
            # --- 1. HERO CASE ---
            {
                "index": 1,
                "case_id": uuid.UUID("716219b7-7d92-4f83-be1e-4047fcdc1651"),
                "is_hero": True,
                "customer_idx": 0,
                "amount": 4500000, # INR 45,000.00
                "method": "upi",
                "error_code": "BANK_TIMEOUT",
                "error_desc": "Bank network timeout during high-value UPI payment",
                "attempt": 1,
                "time_offset_min": 15,
                "target_state": "pending_approval",
            },
            # --- 2-4. ACTIONABLE HIGH PRIORITY (PENDING_APPROVAL) ---
            {
                "index": 2,
                "customer_idx": 1,
                "amount": 2850000, # INR 28,500.00
                "method": "card",
                "error_code": "NETWORK_ERROR",
                "error_desc": "Acquiring bank network connectivity dropped",
                "attempt": 1,
                "time_offset_min": 25,
                "target_state": "pending_approval",
            },
            {
                "index": 3,
                "customer_idx": 2,
                "amount": 1800000, # INR 18,000.00
                "method": "upi",
                "error_code": "AUTHENTICATION_FAILED",
                "error_desc": "Customer 2FA authentication session timed out",
                "attempt": 1,
                "time_offset_min": 40,
                "target_state": "pending_approval",
            },
            {
                "index": 4,
                "customer_idx": 3,
                "amount": 1250000, # INR 12,500.00
                "method": "netbanking",
                "error_code": "BANK_TIMEOUT",
                "error_desc": "Netbanking gateway timeout during settlement",
                "attempt": 1,
                "time_offset_min": 55,
                "target_state": "pending_approval",
            },
            # --- 5-7. ACTIONABLE MEDIUM PRIORITY (PENDING_APPROVAL) ---
            {
                "index": 5,
                "customer_idx": 4,
                "amount": 350000, # INR 3,500.00
                "method": "upi",
                "error_code": "NETWORK_ERROR",
                "error_desc": "NPCI UPI switch response timeout",
                "attempt": 1,
                "time_offset_min": 70,
                "target_state": "pending_approval",
            },
            {
                "index": 6,
                "customer_idx": 5,
                "amount": 220000, # INR 2,200.00
                "method": "card",
                "error_code": "AUTHENTICATION_FAILED",
                "error_desc": "OTP expired during card 3DS challenge",
                "attempt": 1,
                "time_offset_min": 85,
                "target_state": "pending_approval",
            },
            {
                "index": 7,
                "customer_idx": 6,
                "amount": 150000, # INR 1,500.00
                "method": "upi",
                "error_code": "INSUFFICIENT_FUNDS",
                "error_desc": "Payer PSP reported insufficient balance",
                "attempt": 1,
                "time_offset_min": 100,
                "target_state": "pending_approval",
            },
            # --- 8-11. APPROVED & SIMULATED OUTCOMES ---
            {
                "index": 8,
                "customer_idx": 7,
                "amount": 800000, # INR 8,000.00
                "method": "upi",
                "error_code": "NETWORK_ERROR",
                "error_desc": "Timeout on initial switch call",
                "attempt": 1,
                "time_offset_min": 120,
                "target_state": "simulated_recovered",
                "approver": "operator_ananya",
                "approval_reason": "High probability temporary failure; approved for retry",
            },
            {
                "index": 9,
                "customer_idx": 8,
                "amount": 540000, # INR 5,400.00
                "method": "card",
                "error_code": "BANK_TIMEOUT",
                "error_desc": "Issuer bank timed out",
                "attempt": 1,
                "time_offset_min": 140,
                "target_state": "simulated_recovered",
                "approver": "operator_rohit",
                "approval_reason": "Verified issuer status active; approved retry",
            },
            {
                "index": 10,
                "customer_idx": 9,
                "amount": 420000, # INR 4,200.00
                "method": "upi",
                "error_code": "NETWORK_ERROR",
                "error_desc": "Intermittent telecom routing failure",
                "attempt": 1,
                "time_offset_min": 160,
                "target_state": "simulated_failed",
                "approver": "operator_vikram",
                "approval_reason": "Approved standard retry attempt",
            },
            {
                "index": 11,
                "customer_idx": 10,
                "amount": 950000, # INR 9,500.00
                "method": "card",
                "error_code": "AUTHENTICATION_FAILED",
                "error_desc": "Cardholder authentication canceled",
                "attempt": 1,
                "time_offset_min": 180,
                "target_state": "simulated_recovered",
                "approver": "operator_ananya",
                "approval_reason": "Payment link approved; customer completed checkout",
            },
            # --- 12-13. APPROVED READY FOR LIVE DEMO EXECUTION ---
            {
                "index": 12,
                "customer_idx": 11,
                "amount": 1500000, # INR 15,000.00
                "method": "upi",
                "error_code": "NETWORK_ERROR",
                "error_desc": "Bank gateway network connection reset",
                "attempt": 1,
                "time_offset_min": 200,
                "target_state": "approved",
                "approver": "operator_priya",
                "approval_reason": "Ready for live simulated recovery execution during demo",
            },
            {
                "index": 13,
                "customer_idx": 12,
                "amount": 680000, # INR 6,800.00
                "method": "card",
                "error_code": "BANK_TIMEOUT",
                "error_desc": "Acquiring bank timeout",
                "attempt": 1,
                "time_offset_min": 220,
                "target_state": "approved",
                "approver": "operator_rohit",
                "approval_reason": "Approved; ready for interactive execution in UI",
            },
            # --- 14-16. REJECTED CASES (HUMAN AUDIT CONTROLS) ---
            {
                "index": 14,
                "customer_idx": 13,
                "amount": 3200000, # INR 32,000.00
                "method": "card",
                "error_code": "NETWORK_ERROR",
                "error_desc": "Transaction connection reset",
                "attempt": 1,
                "time_offset_min": 240,
                "target_state": "rejected",
                "rejector": "risk_officer_suresh",
                "rejection_reason": "Customer requested order cancellation via support ticket #4819",
            },
            {
                "index": 15,
                "customer_idx": 14,
                "amount": 1400000, # INR 14,000.00
                "method": "upi",
                "error_code": "AUTHENTICATION_FAILED",
                "error_desc": "Authentication rejected by issuing bank",
                "attempt": 1,
                "time_offset_min": 260,
                "target_state": "rejected",
                "rejector": "compliance_lead",
                "rejection_reason": "Suspected unauthorized account access pattern flagged",
            },
            {
                "index": 16,
                "customer_idx": 15,
                "amount": 750000, # INR 7,500.00
                "method": "upi",
                "error_code": "INSUFFICIENT_FUNDS",
                "error_desc": "Insufficient balance on customer account",
                "attempt": 1,
                "time_offset_min": 280,
                "target_state": "rejected",
                "rejector": "operator_ananya",
                "rejection_reason": "Customer confirmed intent to pay offline",
            },
            # --- 17-20. LOW PRIORITY / POLICY BLOCKED / NO_ACTION ---
            {
                "index": 17,
                "customer_idx": 16,
                "amount": 120000, # INR 1,200.00
                "method": "upi",
                "error_code": "PAYMENT_EXPIRED",
                "error_desc": "Payment link validity expired",
                "attempt": 1,
                "time_offset_min": 300,
                "target_state": "analyzed_no_action",
            },
            {
                "index": 18,
                "customer_idx": 17,
                "amount": 85000, # INR 850.00
                "method": "card",
                "error_code": "NETWORK_ERROR",
                "error_desc": "Card network timeout",
                "attempt": 3, # Exceeds max attempts
                "time_offset_min": 320,
                "target_state": "analyzed_no_action",
            },
            {
                "index": 19,
                "customer_idx": 18,
                "amount": 5000000, # INR 50,000.00
                "method": "card",
                "error_code": "FRAUD_SUSPECTED", # Blocked by policy unsupported_failures
                "error_desc": "Suspicious velocity threshold triggered",
                "attempt": 1,
                "time_offset_min": 340,
                "target_state": "analyzed_no_action",
            },
            {
                "index": 20,
                "customer_idx": 19,
                "amount": 45000, # INR 450.00
                "method": "upi",
                "error_code": "ORDER_CANCELLED",
                "error_desc": "Customer cancelled order after multiple failed attempts",
                "attempt": 3,
                "time_offset_min": 360,
                "target_state": "analyzed_no_action",
            },
        ]

        hero_case_info = {}
        created_cases = []

        for spec in cases_spec:
            cust = customer_objs[spec["customer_idx"]]
            failed_time = now - timedelta(minutes=spec["time_offset_min"])

            # A. Order
            order = Order(
                id=uuid.uuid4(),
                merchant_id=merchant.id,
                customer_id=cust.id,
                razorpay_order_id=f"order_demo_{uuid.uuid4().hex[:10]}",
                amount=spec["amount"],
                currency="INR",
                status="attempted",
                created_at=failed_time - timedelta(minutes=2)
            )
            db.add(order)
            db.flush()

            # B. Payment
            payment = Payment(
                id=uuid.uuid4(),
                merchant_id=merchant.id,
                customer_id=cust.id,
                order_id=order.id,
                razorpay_payment_id=f"pay_demo_{uuid.uuid4().hex[:12]}",
                amount=spec["amount"],
                currency="INR",
                method=spec["method"],
                status="failed",
                error_code=spec["error_code"],
                error_description=spec["error_desc"],
                attempt_number=spec["attempt"],
                failed_at=failed_time,
                created_at=failed_time
            )
            db.add(payment)
            db.flush()

            # C. Payment Event (Webhook payload recorded)
            event = PaymentEvent(
                id=uuid.uuid4(),
                payment_id=payment.id,
                event_type="payment.failed",
                razorpay_event_id=f"evt_demo_{uuid.uuid4().hex[:12]}",
                payload={
                    "entity": "event",
                    "event": "payment.failed",
                    "payment_id": payment.razorpay_payment_id,
                    "amount": payment.amount,
                    "currency": payment.currency,
                    "error_code": payment.error_code,
                    "error_description": payment.error_description
                },
                received_at=failed_time,
                processing_status="processed"
            )
            db.add(event)
            db.flush()

            # D. Recovery Case (initial open state)
            recovery_case = RecoveryCase(
                id=spec.get("case_id", uuid.uuid4()),
                payment_id=payment.id,
                status="open",
                amount_at_risk=payment.amount,
                eligible=True,
                eligibility_reason="Eligible for autonomous recovery analysis",
                opened_at=failed_time
            )
            db.add(recovery_case)
            db.commit()

            # E. Real AI & ML Analysis (invokes real ML model and Strategy Optimizer)
            analysis_resp = analyze_recovery_case(db, payment.id, recovery_case.id)
            db.refresh(recovery_case)

            decision = db.query(RecoveryDecision).filter(
                RecoveryDecision.recovery_case_id == recovery_case.id
            ).first()

            # F. Target State Transitions
            target = spec["target_state"]

            if target == "pending_approval":
                # Ensure approval_status is set
                if recovery_case.status != "pending_approval":
                    recovery_case.status = "pending_approval"
                    recovery_case.approval_status = ApprovalStatus.PENDING_APPROVAL.value
                    db.commit()

            elif target == "approved":
                transition_to_approved(
                    db,
                    recovery_case,
                    approved_by=spec["approver"],
                    reason=spec["approval_reason"]
                )
                db.commit()

            elif target == "rejected":
                transition_to_rejected(
                    db,
                    recovery_case,
                    rejected_by=spec["rejector"],
                    reason=spec["rejection_reason"]
                )
                db.commit()

            elif target == "simulated_recovered":
                # 1. Approve
                transition_to_approved(
                    db,
                    recovery_case,
                    approved_by=spec["approver"],
                    reason=spec["approval_reason"]
                )
                # 2. Executing
                transition_to_executing(db, recovery_case)
                # 3. Action record
                action = RecoveryActionModel(
                    recovery_case_id=recovery_case.id,
                    decision_id=decision.id,
                    action_type=decision.recommended_action,
                    status="completed",
                    attempt_number=spec["attempt"],
                    approved_by_policy=True
                )
                db.add(action)
                db.flush()
                # 4. Result record
                result = ActionResult(
                    action_id=action.id,
                    success=True,
                    razorpay_reference=f"pay_sim_{uuid.uuid4().hex[:12]}",
                    previous_payment_status="failed",
                    final_payment_status="captured",
                    recovered_amount=payment.amount,
                    response_payload={"simulated": True, "recovery_status": "captured"}
                )
                db.add(result)
                # 5. Recovered
                transition_to_recovered(db, recovery_case)
                payment.status = "captured"
                db.commit()

            elif target == "simulated_failed":
                # 1. Approve
                transition_to_approved(
                    db,
                    recovery_case,
                    approved_by=spec["approver"],
                    reason=spec["approval_reason"]
                )
                # 2. Executing
                transition_to_executing(db, recovery_case)
                # 3. Action record
                action = RecoveryActionModel(
                    recovery_case_id=recovery_case.id,
                    decision_id=decision.id,
                    action_type=decision.recommended_action,
                    status="failed",
                    attempt_number=spec["attempt"],
                    approved_by_policy=True
                )
                db.add(action)
                db.flush()
                # 4. Result record
                result = ActionResult(
                    action_id=action.id,
                    success=False,
                    razorpay_reference=None,
                    previous_payment_status="failed",
                    final_payment_status="failed",
                    recovered_amount=0,
                    error_code="DOWNSTREAM_GATEWAY_TIMEOUT",
                    error_message="Simulated retry attempted; downstream switch timed out",
                    response_payload={"simulated": True, "recovery_status": "failed"}
                )
                db.add(result)
                # 5. Failed
                transition_to_failed(db, recovery_case)
                db.commit()

            elif target == "analyzed_no_action":
                # Ensure no-action cases have clean None approval status (displays NOT REQUIRED)
                recovery_case.status = "analyzed"
                recovery_case.approval_status = None
                db.commit()

            db.refresh(recovery_case)
            created_cases.append(recovery_case)

            if spec.get("is_hero"):
                hero_case_info = {
                    "case_id": str(recovery_case.id),
                    "payment_id": str(payment.id),
                    "customer_name": cust.name,
                    "amount_minor": payment.amount,
                    "amount_inr": f"₹{payment.amount / 100:,.2f}",
                    "recovery_probability": float(recovery_case.recovery_probability),
                    "expected_recovery_value_minor": recovery_case.expected_recovery_value,
                    "expected_recovery_value_inr": f"₹{recovery_case.expected_recovery_value / 100:,.2f}",
                    "priority_level": recovery_case.priority_level,
                    "recommended_action": decision.recommended_action,
                    "diagnosis": decision.diagnosis,
                    "approval_status": recovery_case.approval_status,
                    "status": recovery_case.status
                }

        print(f"\nSuccessfully seeded {len(created_cases)} deterministic demo recovery cases.")
        return hero_case_info

    except Exception as e:
        db.rollback()
        print(f"Error seeding demo dataset: {e}")
        raise e
    finally:
        db.close()

if __name__ == "__main__":
    hero = seed_demo_dataset()
    print("\n--- HERO CASE SUMMARY ---")
    for k, v in hero.items():
        print(f"  {k}: {v}")

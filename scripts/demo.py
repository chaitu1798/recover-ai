import os
import sys
import json
import uuid
import hmac
import hashlib
import time
import urllib.request
import urllib.error

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app.config import settings

API_URL = "http://backend:8000/api/v1"

def generate_signature(payload_bytes: bytes, secret: str) -> str:
    return hmac.new(
        key=secret.encode('utf-8'),
        msg=payload_bytes,
        digestmod=hashlib.sha256
    ).hexdigest()

def trigger_webhook(payment_id: str, amount: int, error_code: str):
    payload = {
        "entity": "event",
        "event": "payment.failed",
        "contains": ["payment"],
        "id": f"evt_{uuid.uuid4().hex[:14]}",
        "payload": {
            "payment": {
                "entity": {
                    "id": payment_id,
                    "entity": "payment",
                    "amount": amount,
                    "currency": "INR",
                    "status": "failed",
                    "error_code": error_code,
                    "error_description": "Failed for demo purposes",
                    "method": "upi"
                }
            }
        }
    }
    
    payload_bytes = json.dumps(payload).encode('utf-8')
    secret = settings.RAZORPAY_WEBHOOK_SECRET or "dummy_secret"
    signature = generate_signature(payload_bytes, secret)
    
    headers = {
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature
    }
    
    print(f"Triggering webhook for {payment_id} ({error_code}) - amount: {amount}")
    try:
        req = urllib.request.Request(f"{API_URL}/webhooks/razorpay", data=payload_bytes, headers=headers, method="POST")
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            print(f"Response: {response.status} {res_text}")
    except urllib.error.HTTPError as e:
        print(f"Error Response: {e.code} {e.read().decode('utf-8')}")
    except Exception as e:
        print(f"Error: {e}")

def run_demo():
    print("Seeding demo data...")
    
    # 1. High amount, BAD_REQUEST_ERROR (should be NO_ACTION or ESCALATE)
    trigger_webhook(f"pay_{uuid.uuid4().hex[:14]}", 5000000, "BAD_REQUEST_ERROR")
    time.sleep(1)
    
    # 2. Low amount, INSUFFICIENT_FUNDS (should be REMINDER or RETRY)
    trigger_webhook(f"pay_{uuid.uuid4().hex[:14]}", 150000, "INSUFFICIENT_FUNDS")
    time.sleep(1)
    
    # 3. Medium amount, NETWORK_ERROR (should be RETRY)
    trigger_webhook(f"pay_{uuid.uuid4().hex[:14]}", 800000, "NETWORK_ERROR")
    time.sleep(1)
    
    # 4. Low amount, TIMEOUT (should be RETRY)
    trigger_webhook(f"pay_{uuid.uuid4().hex[:14]}", 250000, "TIMEOUT")
    time.sleep(1)
    
    # 5. Very high amount, FRAUD_SUSPECTED (should be NO_ACTION or ESCALATE)
    trigger_webhook(f"pay_{uuid.uuid4().hex[:14]}", 15000000, "FRAUD_SUSPECTED")
    
    print("Demo data seeded. You can now view the dashboard to approve or reject recoveries.")

if __name__ == "__main__":
    run_demo()

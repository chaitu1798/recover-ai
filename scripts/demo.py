import os
import sys
import json
import uuid
import hmac
import hashlib
import time
import urllib.request
import urllib.error

root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
backend_path = os.path.join(root_path, "backend")
if root_path not in sys.path:
    sys.path.append(root_path)
if backend_path not in sys.path:
    sys.path.append(backend_path)

from app.config import settings  # type: ignore

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

from scripts.seed_demo_data import seed_demo_dataset

def run_demo():
    if "--webhook-only" in sys.argv:
        print("Triggering sample Razorpay webhooks...")
        trigger_webhook(f"pay_{uuid.uuid4().hex[:14]}", 800000, "NETWORK_ERROR")
        time.sleep(1)
        trigger_webhook(f"pay_{uuid.uuid4().hex[:14]}", 150000, "INSUFFICIENT_FUNDS")
        return

    print("==================================================")
    print("RECOVERAI BUILDATHON DEMO DATASET GENERATOR")
    print("==================================================")
    hero = seed_demo_dataset()

    print("\n==================================================")
    print("BUILDATHON DEMO HERO CASE")
    print("==================================================")
    for k, v in hero.items():
        print(f"  {k:30}: {v}")
    print("\nDashboard URL: http://localhost:3000")
    print(f"Hero Case URL: http://localhost:3000/recovery/{hero['case_id']}")
    print("==================================================")

if __name__ == "__main__":
    run_demo()

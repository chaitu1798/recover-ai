import hmac
import hashlib
import json
import os
import sys
import uuid
import argparse
import httpx

def main():
    parser = argparse.ArgumentParser(description="Send Razorpay Webhook Simulation")
    default_secret = os.getenv("RAZORPAY_WEBHOOK_SECRET", "test_webhook_secret_123")
    parser.add_argument("--url", default="http://localhost:8000/api/v1/webhooks/razorpay", help="Webhook endpoint URL")
    parser.add_argument("--secret", default=default_secret, help="Webhook secret")
    parser.add_argument("--new-payment", action="store_true", help="Generate a fresh unique payment ID and event ID")
    args = parser.parse_args()

    if not os.path.exists(args.fixture_path):
        print(f"Error: Fixture {args.fixture_path} not found")
        sys.exit(1)

    with open(args.fixture_path, 'r') as f:
        data = json.load(f)

    # Ensure event has an ID
    if "id" not in data or args.new_payment:
        data["id"] = f"evt_{uuid.uuid4().hex[:16]}"

    # Optionally randomize payment ID so each webhook creates a fresh recovery case
    if args.new_payment:
        new_pay_id = f"pay_{uuid.uuid4().hex[:14]}"
        if "payload" in data and "payment" in data["payload"] and "entity" in data["payload"]["payment"]:
            data["payload"]["payment"]["entity"]["id"] = new_pay_id

    payload = json.dumps(data)

    signature = hmac.new(
        key=args.secret.encode('utf-8'),
        msg=payload.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    headers = {
        "Content-Type": "application/json",
        "X-Razorpay-Signature": signature
    }

    try:
        response = httpx.post(args.url, content=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response: {response.json()}")
        except Exception:
            print(f"Response Text: {response.text}")
    except httpx.RequestError as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()

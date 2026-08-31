import hmac
import hashlib
import json
import os
import argparse
import requests

def main():
    parser = argparse.ArgumentParser(description="Test Razorpay Webhook")
    parser.add_argument("fixture_path", help="Path to JSON fixture")
    parser.add_argument("--url", default="http://localhost:8000/api/v1/webhooks/razorpay")
    parser.add_argument("--secret", default="test_secret", help="Webhook secret")
    args = parser.parse_args()

    if not os.path.exists(args.fixture_path):
        print(f"Error: Fixture {args.fixture_path} not found")
        return

    with open(args.fixture_path, 'r') as f:
        payload = f.read()

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
        response = requests.post(args.url, data=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    main()

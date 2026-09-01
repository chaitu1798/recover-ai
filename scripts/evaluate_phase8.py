import os
import sys
import json
import urllib.request
import urllib.error

API_URL = "http://localhost:8000/api/v1"

def check_endpoint(url: str, name: str):
    print(f"Checking {name} at {url}...")
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            res_text = response.read().decode('utf-8')
            print(f"[{name}] OK - {response.status}: {res_text}")
            return True
    except urllib.error.HTTPError as e:
        print(f"[{name}] FAIL - HTTP {e.code}: {e.read().decode('utf-8')}")
        return False
    except Exception as e:
        print(f"[{name}] ERROR - {e}")
        return False

def run_evaluation():
    print("--- Phase 8 Evaluation ---")
    
    # 1. Health check
    health_ok = check_endpoint(f"{API_URL}/health", "Liveness")
    
    # 2. Ready check
    ready_ok = check_endpoint(f"{API_URL}/ready", "Readiness")
    
    # 3. Validation Error Handler
    print("Checking Global Exception Handler (422)...")
    try:
        req = urllib.request.Request(f"{API_URL}/recovery/cases/invalid-uuid", method="GET")
        with urllib.request.urlopen(req) as response:
            pass # Should fail
    except urllib.error.HTTPError as e:
        if e.code == 422:
            try:
                err_data = json.loads(e.read().decode('utf-8'))
                if "request_id" in err_data.get("error", {}):
                    print("[Validation Handler] OK - request_id present")
                else:
                    print("[Validation Handler] FAIL - Missing request_id in 422 response")
            except Exception:
                print("[Validation Handler] FAIL - Could not parse error response")
        else:
            print(f"[Validation Handler] FAIL - Expected 422, got {e.code}")
            
    print("--- Evaluation Complete ---")
    
if __name__ == "__main__":
    run_evaluation()

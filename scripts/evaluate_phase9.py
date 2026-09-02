import urllib.request
import json
import time

def evaluate_phase9():
    print("Evaluating Phase 9 Intelligence")
    print("--------------------------------")
    
    dashboard_url = "http://localhost:8000/api/v1/dashboard"
    
    try:
        # Evaluate Strategy Analytics
        print("1. Checking Strategy Analytics...")
        req = urllib.request.Request(f"{dashboard_url}/strategy-analytics")
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    print("   PASS - Strategy Analytics API responsive")
                    print("   Data:", json.loads(response.read().decode()))
                else:
                    print("   FAIL - Strategy Analytics API returned", response.status)
        except Exception as e:
            print("   FAIL - Strategy Analytics API failed:", e)
            
        # Evaluate Expected vs Actual
        print("2. Checking Expected vs Actual Analytics...")
        req = urllib.request.Request(f"{dashboard_url}/expected-vs-actual")
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    print("   PASS - Expected vs Actual API responsive")
                    print("   Data:", json.loads(response.read().decode()))
                else:
                    print("   FAIL - Expected vs Actual API returned", response.status)
        except Exception as e:
            print("   FAIL - Expected vs Actual API failed:", e)
            
        # Evaluate ML Monitoring
        print("3. Checking ML Monitoring...")
        req = urllib.request.Request(f"{dashboard_url}/ml-monitoring")
        try:
            with urllib.request.urlopen(req) as response:
                if response.status == 200:
                    print("   PASS - ML Monitoring API responsive")
                    print("   Data:", json.loads(response.read().decode()))
                else:
                    print("   FAIL - ML Monitoring API returned", response.status)
        except Exception as e:
            print("   FAIL - ML Monitoring API failed:", e)
            
        print("\nPhase 9 Evaluation Complete.")
        
    except Exception as e:
        print(f"Error connecting to backend: {e}")
        print("Make sure the backend is running at http://localhost:8000")

if __name__ == "__main__":
    evaluate_phase9()

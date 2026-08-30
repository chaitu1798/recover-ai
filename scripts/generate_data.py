import csv
import random
import uuid
from datetime import datetime, timedelta

SEED = 42
random.seed(SEED)

TOTAL_RECORDS = 2000
TRAIN_RATIO = 0.6
VAL_RATIO = 0.15
TEST_RATIO = 0.25  # guarantees 500 test records

def generate_customer():
    return {
        "customer_id": str(uuid.uuid4()),
        "tenure_days": random.randint(1, 1000),
        "total_successes": random.randint(0, 20),
        "historical_failure_rate": random.uniform(0.0, 0.5)
    }

def generate_record(customer):
    payment_id = str(uuid.uuid4())
    
    amount = random.randint(100, 50000) * 100
    currency = "INR"
    
    payment_methods = ["UPI", "CARD", "NETBANKING", "WALLET"]
    method_weights = [0.6, 0.25, 0.1, 0.05]
    payment_method = random.choices(payment_methods, method_weights)[0]
    
    failure_reasons = [
        "BANK_TIMEOUT",
        "NETWORK_ERROR",
        "INSUFFICIENT_FUNDS",
        "CUSTOMER_ABANDONED",
        "PAYMENT_EXPIRED",
        "INVALID_PAYMENT_STATE",
        "OTHER"
    ]
    reason_weights = [0.3, 0.2, 0.15, 0.15, 0.05, 0.05, 0.1]
    failure_reason = random.choices(failure_reasons, reason_weights)[0]
    
    payment_status = "failed"
    
    attempt_number = random.choices([1, 2, 3, 4], [0.7, 0.2, 0.08, 0.02])[0]
    previous_successes = customer["total_successes"]
    previous_failures = int(customer["total_successes"] * customer["historical_failure_rate"]) + (attempt_number - 1)
    
    time_since_failure_minutes = random.randint(1, 1440)
    
    if previous_failures + previous_successes == 0:
        historical_recovery_rate = 0.0
    else:
        historical_recovery_rate = round(min(1.0, random.uniform(0.1, 0.9)), 2)
        
    # Controlled ground-truth logic
    recoverable_prob = 0.45
    
    if failure_reason in ["BANK_TIMEOUT", "NETWORK_ERROR"]:
        recoverable_prob += 0.3
    if failure_reason in ["PAYMENT_EXPIRED", "INVALID_PAYMENT_STATE"]:
        recoverable_prob -= 0.4
    if failure_reason == "INSUFFICIENT_FUNDS":
        recoverable_prob -= 0.1
        
    if previous_successes > 2:
        recoverable_prob += 0.1
    
    if attempt_number > 2:
        recoverable_prob -= 0.2
        
    if time_since_failure_minutes > 720:
        recoverable_prob -= 0.15
        
    # Add controlled noise
    recoverable_prob += random.uniform(-0.15, 0.15)
    
    recoverable_ground_truth = "TRUE" if recoverable_prob > 0.45 else "FALSE"
    
    if recoverable_ground_truth == "TRUE":
        if failure_reason in ["BANK_TIMEOUT", "NETWORK_ERROR"]:
            expected_recovery_action = "RETRY"
        elif failure_reason == "INSUFFICIENT_FUNDS":
            expected_recovery_action = "REMINDER"
        else:
            expected_recovery_action = "PAYMENT_LINK"
            
        simulated_recovery_outcome = "SUCCESS" if random.random() < 0.75 else "FAILURE"
        simulated_recovered_amount = amount if simulated_recovery_outcome == "SUCCESS" else 0
    else:
        expected_recovery_action = "NO_ACTION"
        simulated_recovery_outcome = "FAILURE"
        simulated_recovered_amount = 0
        
    created_at = (datetime.now() - timedelta(minutes=time_since_failure_minutes)).isoformat()
    
    return {
        "payment_id": payment_id,
        "customer_id": customer["customer_id"],
        "amount": amount,
        "currency": currency,
        "payment_method": payment_method,
        "payment_status": payment_status,
        "failure_reason": failure_reason,
        "attempt_number": attempt_number,
        "previous_successes": previous_successes,
        "previous_failures": previous_failures,
        "customer_tenure_days": customer["tenure_days"],
        "time_since_failure_minutes": time_since_failure_minutes,
        "historical_recovery_rate": historical_recovery_rate,
        "recoverable_ground_truth": recoverable_ground_truth,
        "expected_recovery_action": expected_recovery_action,
        "simulated_recovery_outcome": simulated_recovery_outcome,
        "simulated_recovered_amount": simulated_recovered_amount,
        "created_at": created_at
    }

def main():
    # To prevent leakage, generate customers first, then assign them to splits
    num_customers = 800
    customers = [generate_customer() for _ in range(num_customers)]
    
    # Customer split
    train_cust = customers[:int(num_customers * TRAIN_RATIO)]
    val_cust = customers[int(num_customers * TRAIN_RATIO):int(num_customers * (TRAIN_RATIO + VAL_RATIO))]
    test_cust = customers[int(num_customers * (TRAIN_RATIO + VAL_RATIO)):]
    
    # Target allocations
    # Exact counts: Train=1200, Val=300, Test=500
    
    def generate_for_split(custList, count):
        records = []
        for _ in range(count):
            c = random.choice(custList)
            records.append(generate_record(c))
        return records
        
    train = generate_for_split(train_cust, 1200)
    val = generate_for_split(val_cust, 300)
    test = generate_for_split(test_cust, 500)
    
    records = train + val + test
    
    keys = records[0].keys()
    
    def write_csv(filename, data):
        with open(filename, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(data)
            
    write_csv("data/synthetic/payments.csv", records)
    write_csv("data/evaluation/train.csv", train)
    write_csv("data/evaluation/validation.csv", val)
    write_csv("data/evaluation/test.csv", test)
    print(f"Generated {len(records)} records successfully (Customer-aware split).")

if __name__ == "__main__":
    main()

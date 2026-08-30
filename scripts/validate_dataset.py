import csv
import sys

def validate():
    def read_csv(path):
        with open(path, "r", encoding="utf-8") as f:
            return list(csv.DictReader(f))
            
    try:
        full = read_csv("data/synthetic/payments.csv")
        train = read_csv("data/evaluation/train.csv")
        val = read_csv("data/evaluation/validation.csv")
        test = read_csv("data/evaluation/test.csv")
    except Exception as e:
        print(f"Error reading dataset files: {e}")
        return False
        
    print("Total records: {}".format(len(full)))
    print("Train: {}".format(len(train)))
    print("Validation: {}".format(len(val)))
    print("Test: {}\n".format(len(test)))
    
    payment_ids = set()
    duplicate_ids = 0
    invalid_amounts = 0
    invalid_recovered_amounts = 0
    invalid_actions = 0
    
    recoverable_count = 0
    non_recoverable_count = 0
    
    failure_reasons_dist = {}
    payment_method_dist = {}
    action_dist = {}
    
    allowed_actions = {"RETRY", "PAYMENT_LINK", "REMINDER", "ESCALATE", "NO_ACTION"}
    
    for row in full:
        pid = row["payment_id"]
        if pid in payment_ids:
            duplicate_ids += 1
        payment_ids.add(pid)
        
        if int(row["amount"]) <= 0:
            invalid_amounts += 1
            
        rec_amt = int(row["simulated_recovered_amount"])
        if rec_amt < 0 or rec_amt > int(row["amount"]):
            invalid_recovered_amounts += 1
            
        if row["expected_recovery_action"] not in allowed_actions:
            invalid_actions += 1
            
        if row["recoverable_ground_truth"] == "TRUE":
            recoverable_count += 1
        else:
            non_recoverable_count += 1
            
        fr = row["failure_reason"]
        failure_reasons_dist[fr] = failure_reasons_dist.get(fr, 0) + 1
        
        pm = row["payment_method"]
        payment_method_dist[pm] = payment_method_dist.get(pm, 0) + 1
        
        act = row["expected_recovery_action"]
        action_dist[act] = action_dist.get(act, 0) + 1
            
    train_ids = {r["customer_id"] for r in train}
    val_ids = {r["customer_id"] for r in val}
    test_ids = {r["customer_id"] for r in test}
    
    train_test_overlap = len(train_ids.intersection(test_ids))
    val_test_overlap = len(val_ids.intersection(test_ids))
    
    rec_perc = (recoverable_count / len(full)) * 100 if len(full) > 0 else 0
    
    print(f"Recoverable: {recoverable_count}")
    print(f"Non-recoverable: {non_recoverable_count}")
    print(f"Recovery percentage: {rec_perc:.2f}%\n")
    
    print("Failure reason distribution:")
    for k, v in failure_reasons_dist.items():
        print(f"  {k}: {v}")
    
    print("\nPayment method distribution:")
    for k, v in payment_method_dist.items():
        print(f"  {k}: {v}")
        
    print("\nAction distribution:")
    for k, v in action_dist.items():
        print(f"  {k}: {v}")
    
    print(f"\nDuplicate IDs: {duplicate_ids}")
    print(f"Invalid amounts: {invalid_amounts}")
    print(f"Invalid recovered amounts: {invalid_recovered_amounts}")
    print(f"Invalid actions: {invalid_actions}")
    print(f"Train/Test overlap (customer): {train_test_overlap}")
    print(f"Validation/Test overlap (customer): {val_test_overlap}\n")
    
    passed = (
        len(full) == 2000 and
        len(train) == 1200 and
        len(val) == 300 and
        len(test) == 500 and
        duplicate_ids == 0 and
        invalid_amounts == 0 and
        invalid_recovered_amounts == 0 and
        invalid_actions == 0 and
        train_test_overlap == 0 and
        val_test_overlap == 0
    )
    
    print(f"Status: {'PASS' if passed else 'FAIL'}")
    return passed

if __name__ == "__main__":
    if not validate():
        sys.exit(1)

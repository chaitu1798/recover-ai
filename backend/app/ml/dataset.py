import pandas as pd

LEAKY_COLUMNS = [
    "expected_recovery_action",
    "simulated_recovery_outcome",
    "simulated_recovered_amount",
    "created_at",
    "payment_id",
    "customer_id",
    "payment_status",  # excluded because it's always 'failed' for this dataset
]

TARGET_COLUMN = "recoverable_ground_truth"

def load_data(file_path: str):
    """
    Load dataset from CSV and separate features from target.
    Also drops all leaky/non-predictive columns.
    """
    df = pd.read_csv(file_path)
    
    # Target conversion
    if TARGET_COLUMN in df.columns:
        y = df[TARGET_COLUMN].apply(lambda x: 1 if str(x).upper() == 'TRUE' else 0)
    else:
        y = None
        
    # Drop target and leaky columns from features
    columns_to_drop = LEAKY_COLUMNS + [TARGET_COLUMN]
    existing_cols_to_drop = [col for col in columns_to_drop if col in df.columns]
    
    X = df.drop(columns=existing_cols_to_drop)
    
    return X, y

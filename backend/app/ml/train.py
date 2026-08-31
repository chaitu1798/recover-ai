import os
import joblib
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from .dataset import load_data
from .features import build_preprocessor
from .model_registry import save_model_metadata

def train_model(data_dir: str, output_dir: str):
    """
    Trains the recovery prediction model using the training dataset.
    """
    train_path = os.path.join(data_dir, "evaluation", "train.csv")
    val_path = os.path.join(data_dir, "evaluation", "validation.csv")
    test_path = os.path.join(data_dir, "evaluation", "test.csv")
    
    # Load data
    X_train, y_train = load_data(train_path)
    X_val, y_val = load_data(val_path)
    X_test, y_test = load_data(test_path)
    
    print(f"Loaded {len(X_train)} training records.")
    
    # Build pipeline
    preprocessor = build_preprocessor()
    
    # Start with natural distribution (class_weight=None)
    classifier = LogisticRegression(random_state=42, class_weight=None, max_iter=1000)
    
    pipeline = Pipeline(steps=[
        ("preprocessor", preprocessor),
        ("classifier", classifier)
    ])
    
    # Fit the pipeline
    print("Training Logistic Regression model...")
    pipeline.fit(X_train, y_train)
    
    # Save model artifact
    os.makedirs(output_dir, exist_ok=True)
    model_path = os.path.join(output_dir, "recovery_model.joblib")
    joblib.dump(pipeline, model_path)
    print(f"Model saved to {model_path}")
    
    # Save metadata
    # The actual threshold will be determined during evaluation
    metadata = {
        "model_name": "logistic_regression",
        "model_version": "1.0.0",
        "training_seed": 42,
        "features": list(X_train.columns),
        "target": "recoverable_ground_truth",
        "train_records": len(X_train),
        "validation_records": len(X_val),
        "test_records": len(X_test),
        "threshold": 0.50 # Default, will be updated by evaluation
    }
    save_model_metadata(metadata)
    print("Model metadata saved.")
    
    return pipeline, metadata

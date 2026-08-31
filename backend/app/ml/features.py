import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.impute import SimpleImputer

# Define numerical and categorical columns
NUMERICAL_FEATURES = [
    "amount",
    "attempt_number",
    "previous_successes",
    "previous_failures",
    "customer_tenure_days",
    "time_since_failure_minutes",
    "historical_recovery_rate"
]

CATEGORICAL_FEATURES = [
    "currency",
    "payment_method",
    "failure_reason"
]

def build_preprocessor() -> ColumnTransformer:
    """
    Builds and returns a scikit-learn ColumnTransformer for feature engineering.
    """
    numeric_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("imputer", SimpleImputer(strategy="constant", fill_value="missing")),
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUMERICAL_FEATURES),
            ("cat", categorical_transformer, CATEGORICAL_FEATURES)
        ]
    )
    
    return preprocessor

def get_feature_names(preprocessor, X_cols):
    """
    Extracts feature names from the preprocessor after it has been fitted.
    """
    # This is a bit tricky with ColumnTransformer in older sklearn versions,
    # but in newer versions (>=1.0), get_feature_names_out is available.
    try:
        return list(preprocessor.get_feature_names_out())
    except AttributeError:
        # Fallback for older versions if needed, though requirements specify scikit-learn>=1.3.0
        return []

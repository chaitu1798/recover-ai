import os
import pytest
from app.ml.train import train_model

def test_reproducibility(tmp_path):
    # Need access to the data directory. 
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    data_dir = os.path.join(base_dir, "data")
    
    if not os.path.exists(os.path.join(data_dir, "evaluation", "train.csv")):
        pytest.skip("Training data not found.")
        
    out1 = os.path.join(tmp_path, "run1")
    out2 = os.path.join(tmp_path, "run2")
    
    # Run 1
    pipe1, meta1 = train_model(data_dir, out1)
    
    # Run 2
    pipe2, meta2 = train_model(data_dir, out2)
    
    # The models should have identical coefficients since random_state=42 is used
    coef1 = pipe1.named_steps["classifier"].coef_
    coef2 = pipe2.named_steps["classifier"].coef_
    
    assert (coef1 == coef2).all(), "Model coefficients are not reproducible!"

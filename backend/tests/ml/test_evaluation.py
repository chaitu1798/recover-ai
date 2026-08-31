import os
import pytest
from app.ml.evaluate import evaluate_model

def test_evaluation_runs(tmp_path):
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    data_dir = os.path.join(base_dir, "data")
    models_dir = os.path.join(base_dir, "models")
    
    if not os.path.exists(os.path.join(models_dir, "recovery_model.joblib")):
        pytest.skip("Model not found. Run training first.")
        
    out_dir = os.path.join(tmp_path, "results")
    
    # Should run without crashing and produce files
    evaluate_model(data_dir, out_dir, models_dir)
    
    assert os.path.exists(os.path.join(out_dir, "metrics.json"))
    assert os.path.exists(os.path.join(out_dir, "evaluation_report.md"))
    assert os.path.exists(os.path.join(out_dir, "confusion_matrix.png"))
    assert os.path.exists(os.path.join(out_dir, "roc_curve.png"))

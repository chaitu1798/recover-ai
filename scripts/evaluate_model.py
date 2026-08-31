import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.ml.evaluate import evaluate_model

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(base_dir, "data")
    output_dir = os.path.join(base_dir, "experiments", "results")
    models_dir = os.path.join(base_dir, "models")
    
    print("Starting Phase 4 Evaluation Pipeline...")
    evaluate_model(data_dir=data_dir, output_dir=output_dir, models_dir=models_dir)
    print("Evaluation Pipeline Complete.")

import os
import sys

# Ensure backend can be imported
sys.path.append(os.path.join(os.path.dirname(__file__), "..", "backend"))

from app.ml.train import train_model

if __name__ == "__main__":
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(base_dir, "data")
    models_dir = os.path.join(base_dir, "models")
    
    print("Starting Phase 4 Training Pipeline...")
    train_model(data_dir=data_dir, output_dir=models_dir)
    print("Training Pipeline Complete.")

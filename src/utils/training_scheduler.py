import schedule
import time
import os
from src.ai.model_trainer import ModelTrainer
from datetime import datetime

def train_models():
    """Train models using collected feedback data"""
    print(f"Starting scheduled model training at {datetime.now().isoformat()}")
    trainer = ModelTrainer()
    success = trainer.train_model(epochs=15)
    
    if success:
        print("Model training completed successfully")
    else:
        print("Model training failed or insufficient data")
        
    print(f"Finished scheduled model training at {datetime.now().isoformat()}")

def setup_scheduler(frequency_hours=24):
    """Set up the scheduler to run training periodically"""
    schedule.every(frequency_hours).hours.do(train_models)
    
    print(f"Training scheduler set up to run every {frequency_hours} hours")
    print("Scheduler running. Press Ctrl+C to exit.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    except KeyboardInterrupt:
        print("Scheduler stopped.")

if __name__ == "__main__":
    # If run directly, start the scheduler
    setup_scheduler()
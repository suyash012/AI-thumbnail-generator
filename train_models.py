import argparse
from src.ai.model_trainer import ModelTrainer
from src.utils.training_scheduler import setup_scheduler

def parse_args():
    parser = argparse.ArgumentParser(description="Train thumbnail generation models")
    parser.add_argument('--scheduler', action='store_true', 
                      help='Run as a scheduled task instead of immediate training')
    parser.add_argument('--hours', type=int, default=24,
                      help='Hours between scheduled training (default: 24)')
    parser.add_argument('--epochs', type=int, default=10,
                      help='Number of epochs for training (default: 10)')
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_args()
    
    if args.scheduler:
        print(f"Setting up scheduled training every {args.hours} hours")
        setup_scheduler(frequency_hours=args.hours)
    else:
        print("Starting immediate model training")
        trainer = ModelTrainer()
        trainer.train_model(epochs=args.epochs)
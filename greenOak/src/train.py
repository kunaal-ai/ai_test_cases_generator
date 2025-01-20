import argparse
import torch
from pathlib import Path
import json
import logging
from src.model import TestCaseGenerator
from src.trainer import TestCaseTrainer
from src.dataset import TestCaseDataset

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main(args):
    # Set device
    device = "cuda" if torch.cuda.is_available() else "cpu"
    logger.info(f"Using device: {device}")

    # Initialize model
    logger.info("Initializing model...")
    model = TestCaseGenerator(model_name=args.model_name, device=device)

    # Load datasets
    logger.info("Loading datasets...")
    train_dataset = TestCaseDataset(
        data_path=args.train_data,
        tokenizer=model.tokenizer,
        max_length=args.max_length
    )
    val_dataset = TestCaseDataset(
        data_path=args.val_data,
        tokenizer=model.tokenizer,
        max_length=args.max_length
    )

    logger.info(f"Train dataset size: {len(train_dataset)}")
    logger.info(f"Validation dataset size: {len(val_dataset)}")

    # Initialize trainer
    trainer = TestCaseTrainer(
        model=model,
        train_dataset=train_dataset,
        val_dataset=val_dataset,
        learning_rate=args.learning_rate,
        batch_size=args.batch_size,
        num_epochs=args.num_epochs,
        warmup_steps=args.warmup_steps,
        logging_steps=args.logging_steps,
        save_steps=args.save_steps,
        output_dir=args.output_dir
    )

    # Start training
    logger.info("Starting training...")
    trainer.train()
    logger.info("Training completed!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train the test case generator model")
    
    # Data arguments
    parser.add_argument("--train_data", type=str, required=True, help="Path to training data")
    parser.add_argument("--val_data", type=str, required=True, help="Path to validation data")
    
    # Model arguments
    parser.add_argument("--model_name", type=str, default="t5-base", help="Base model name")
    parser.add_argument("--max_length", type=int, default=512, help="Maximum sequence length")
    
    # Training arguments
    parser.add_argument("--learning_rate", type=float, default=2e-5, help="Learning rate")
    parser.add_argument("--batch_size", type=int, default=8, help="Batch size")
    parser.add_argument("--num_epochs", type=int, default=3, help="Number of epochs")
    parser.add_argument("--warmup_steps", type=int, default=0, help="Number of warmup steps")
    parser.add_argument("--logging_steps", type=int, default=100, help="Logging frequency")
    parser.add_argument("--save_steps", type=int, default=1000, help="Model saving frequency")
    parser.add_argument("--output_dir", type=str, default="models", help="Output directory for models")

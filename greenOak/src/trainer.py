import torch
from torch.utils.data import DataLoader
from transformers import AdamW, get_linear_schedule_with_warmup
from typing import Dict, List
import wandb
import logging
from tqdm import tqdm
import numpy as np
from sklearn.metrics import precision_recall_fscore_support
from .model import TestCaseGenerator
from .dataset import TestCaseDataset
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

class TestCaseTrainer:
    def __init__(self,
                 model: TestCaseGenerator,
                 train_dataset: TestCaseDataset,
                 val_dataset: TestCaseDataset,
                 learning_rate: float = 2e-5,
                 batch_size: int = 8,
                 num_epochs: int = 3,
                 warmup_steps: int = 0,
                 logging_steps: int = 100,
                 save_steps: int = 1000,
                 output_dir: str = "models"):
        
        self.model = model
        self.device = model.device
        self.train_dataloader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        self.val_dataloader = DataLoader(val_dataset, batch_size=batch_size)
        
        self.optimizer = AdamW(model.parameters(), lr=learning_rate)
        self.scheduler = get_linear_schedule_with_warmup(
            self.optimizer,
            num_warmup_steps=warmup_steps,
            num_training_steps=len(self.train_dataloader) * num_epochs
        )
        
        self.num_epochs = num_epochs
        self.logging_steps = logging_steps
        self.save_steps = save_steps
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Metrics tracking
        self.train_losses = []
        self.val_losses = []
        self.metrics_history = {
            'precision': [],
            'recall': [],
            'f1': []
        }

    def train(self):
        """Train the model"""
        wandb.init(project="greenoak-test-generator")
        global_step = 0
        best_val_loss = float('inf')
        
        for epoch in range(self.num_epochs):
            print(f"\nEpoch {epoch + 1}/{self.num_epochs}")
            epoch_loss = 0
            self.model.train()
            
            # Training loop
            progress_bar = tqdm(self.train_dataloader, desc="Training")
            for step, batch in enumerate(progress_bar):
                batch = {k: v.to(self.device) for k, v in batch.items()}
                
                # Training step
                outputs = self.model.train_step(batch)
                loss = outputs["loss"]
                epoch_loss += loss
                
                # Backward pass
                self.optimizer.zero_grad()
                loss.backward()
                self.optimizer.step()
                self.scheduler.step()
                
                # Logging
                if global_step % self.logging_steps == 0:
                    self.log_metrics(global_step, loss, outputs)
                
                # Save model
                if global_step % self.save_steps == 0:
                    self.save_checkpoint(global_step)
                
                global_step += 1
                progress_bar.set_postfix({'loss': loss})
            
            # Validation
            val_loss, metrics = self.evaluate()
            self.train_losses.append(epoch_loss / len(self.train_dataloader))
            self.val_losses.append(val_loss)
            
            # Update metrics history
            for metric, value in metrics.items():
                self.metrics_history[metric].append(value)
            
            # Save best model
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                self.save_checkpoint('best')
            
            # Generate and save visualizations
            self.generate_visualizations(epoch)
            
            # Log epoch metrics
            wandb.log({
                'epoch': epoch,
                'train_loss': epoch_loss / len(self.train_dataloader),
                'val_loss': val_loss,
                **metrics
            })

    def evaluate(self):
        """Evaluate the model"""
        self.model.eval()
        val_loss = 0
        all_preds = []
        all_labels = []
        
        with torch.no_grad():
            for batch in tqdm(self.val_dataloader, desc="Evaluating"):
                batch = {k: v.to(self.device) for k, v in batch.items()}
                outputs = self.model.train_step(batch)
                val_loss += outputs["loss"]
                
                # Convert logits to predictions
                preds = torch.argmax(outputs["logits"], dim=-1)
                all_preds.extend(preds.cpu().numpy())
                all_labels.extend(batch["labels"].cpu().numpy())
        
        # Calculate metrics
        precision, recall, f1, _ = precision_recall_fscore_support(
            all_labels,
            all_preds,
            average='weighted'
        )
        
        return val_loss / len(self.val_dataloader), {
            'precision': precision,
            'recall': recall,
            'f1': f1
        }

    def generate_visualizations(self, epoch: int):
        """Generate training visualizations"""
        vis_dir = self.output_dir / 'visualizations'
        vis_dir.mkdir(exist_ok=True)
        
        # Loss curves
        plt.figure(figsize=(10, 6))
        plt.plot(self.train_losses, label='Training Loss')
        plt.plot(self.val_losses, label='Validation Loss')
        plt.title('Training and Validation Loss')
        plt.xlabel('Epoch')
        plt.ylabel('Loss')
        plt.legend()
        plt.savefig(vis_dir / f'loss_curves_epoch_{epoch}.png')
        plt.close()
        
        # Metrics over time
        plt.figure(figsize=(12, 6))
        for metric, values in self.metrics_history.items():
            plt.plot(values, label=metric.capitalize())
        plt.title('Metrics Over Time')
        plt.xlabel('Epoch')
        plt.ylabel('Score')
        plt.legend()
        plt.savefig(vis_dir / f'metrics_epoch_{epoch}.png')
        plt.close()
        
        # Learning rate schedule
        plt.figure(figsize=(10, 6))
        lrs = [self.scheduler.get_lr()[0] for _ in range(len(self.train_dataloader))]
        plt.plot(lrs)
        plt.title('Learning Rate Schedule')
        plt.xlabel('Step')
        plt.ylabel('Learning Rate')
        plt.savefig(vis_dir / f'lr_schedule_epoch_{epoch}.png')
        plt.close()

    def log_metrics(self, step: int, loss: float, outputs: Dict):
        """Log metrics to wandb"""
        wandb.log({
            'step': step,
            'loss': loss,
            'learning_rate': self.scheduler.get_lr()[0]
        })

    def save_checkpoint(self, step):
        """Save model checkpoint"""
        checkpoint_dir = self.output_dir / f'checkpoint-{step}'
        checkpoint_dir.mkdir(exist_ok=True)
        self.model.save_model(str(checkpoint_dir))
        
        # Save optimizer and scheduler
        torch.save({
            'optimizer': self.optimizer.state_dict(),
            'scheduler': self.scheduler.state_dict()
        }, checkpoint_dir / 'optimizer.pt')

import torch
from torch.utils.data import Dataset
from typing import Dict, List, Optional
import json
import pandas as pd
from pathlib import Path
import logging

class TestCaseDataset(Dataset):
    def __init__(self, 
                 data_path: str,
                 tokenizer,
                 max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.data = self.load_data(data_path)

    def load_data(self, data_path: str) -> List[Dict]:
        """Load and preprocess the dataset"""
        data_path = Path(data_path)
        if not data_path.exists():
            raise FileNotFoundError(f"Data file not found: {data_path}")

        if data_path.suffix == '.json':
            with open(data_path) as f:
                data = json.load(f)
        elif data_path.suffix == '.csv':
            data = pd.read_csv(data_path).to_dict('records')
        else:
            raise ValueError(f"Unsupported file format: {data_path.suffix}")

        processed_data = []
        for item in data:
            try:
                # Format input text
                input_text = f"[FEATURE] {item['feature_description']} "
                input_text += f"[TYPE] {item['feature_type']} {item['test_type']} "
                if 'domain' in item and item['domain']:
                    input_text += f"[DOMAIN] {item['domain']}"

                # Format target text
                target_text = ""
                if 'scenario' in item:
                    target_text += f"[SCENARIO] {item['scenario']} "
                if 'steps' in item:
                    target_text += f"[STEPS] {' '.join(item['steps'])} "
                if 'expected_results' in item:
                    target_text += f"[EXPECTED] {' '.join(item['expected_results'])} "
                if 'test_data' in item:
                    target_text += f"[DATA] {json.dumps(item['test_data'])} "
                if 'requirements' in item:
                    target_text += f"[REQUIREMENTS] {' '.join(item['requirements'])}"

                processed_data.append({
                    'input_text': input_text.strip(),
                    'target_text': target_text.strip()
                })
            except Exception as e:
                logging.error(f"Error processing data item: {str(e)}")
                continue

        return processed_data

    def __len__(self) -> int:
        return len(self.data)

    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        item = self.data[idx]
        
        # Tokenize input and target
        input_encoding = self.tokenizer(
            item['input_text'],
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )
        
        target_encoding = self.tokenizer(
            item['target_text'],
            max_length=self.max_length,
            padding='max_length',
            truncation=True,
            return_tensors='pt'
        )

        return {
            'input_ids': input_encoding['input_ids'].squeeze(),
            'attention_mask': input_encoding['attention_mask'].squeeze(),
            'labels': target_encoding['input_ids'].squeeze()
        }

class TestCaseCollator:
    def __init__(self, tokenizer, max_length: int = 512):
        self.tokenizer = tokenizer
        self.max_length = max_length

    def __call__(self, batch: List[Dict]) -> Dict[str, torch.Tensor]:
        input_ids = torch.stack([item['input_ids'] for item in batch])
        attention_mask = torch.stack([item['attention_mask'] for item in batch])
        labels = torch.stack([item['labels'] for item in batch])

        return {
            'input_ids': input_ids,
            'attention_mask': attention_mask,
            'labels': labels
        }

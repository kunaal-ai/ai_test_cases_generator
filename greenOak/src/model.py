import torch
import torch.nn as nn
from transformers import T5ForConditionalGeneration, T5Tokenizer
from typing import Dict, List, Optional
import json
import logging

class TestCaseGenerator(nn.Module):
    def __init__(self, model_name: str = "t5-base", device: str = "cuda" if torch.cuda.is_available() else "cpu"):
        super().__init__()
        self.device = device
        self.model = T5ForConditionalGeneration.from_pretrained(model_name).to(device)
        self.tokenizer = T5Tokenizer.from_pretrained(model_name)
        
        # Special tokens for test case generation
        special_tokens = {
            'additional_special_tokens': [
                '[FEATURE]', '[DOMAIN]', '[TYPE]', '[SCENARIO]',
                '[STEPS]', '[EXPECTED]', '[DATA]', '[REQUIREMENTS]'
            ]
        }
        self.tokenizer.add_special_tokens(special_tokens)
        self.model.resize_token_embeddings(len(self.tokenizer))

    def format_input(self, 
                    feature_description: str,
                    feature_type: str,
                    test_type: str,
                    domain: Optional[str] = None) -> str:
        """Format the input for the model"""
        input_text = f"[FEATURE] {feature_description} "
        input_text += f"[TYPE] {feature_type} {test_type} "
        if domain:
            input_text += f"[DOMAIN] {domain}"
        return input_text

    def format_output(self, output_text: str) -> Dict:
        """Convert model output to structured test case format"""
        try:
            # Basic cleaning and formatting
            output_text = output_text.replace("<pad>", "").replace("</s>", "")
            
            # Extract sections using special tokens
            sections = {}
            for token in ['[SCENARIO]', '[STEPS]', '[EXPECTED]', '[DATA]', '[REQUIREMENTS]']:
                if token in output_text:
                    parts = output_text.split(token)
                    for part in parts[1:]:
                        end_idx = part.find('[')
                        if end_idx == -1:
                            end_idx = len(part)
                        sections[token] = part[:end_idx].strip()
            
            # Structure the output
            return {
                "scenario": sections.get('[SCENARIO]', ''),
                "steps": [s.strip() for s in sections.get('[STEPS]', '').split('\n') if s.strip()],
                "expected_results": [e.strip() for e in sections.get('[EXPECTED]', '').split('\n') if e.strip()],
                "test_data": json.loads(sections.get('[DATA]', '{}')),
                "requirements": [r.strip() for r in sections.get('[REQUIREMENTS]', '').split('\n') if r.strip()]
            }
        except Exception as e:
            logging.error(f"Error formatting output: {str(e)}")
            return {}

    def generate(self,
                feature_description: str,
                feature_type: str,
                test_type: str,
                domain: Optional[str] = None,
                num_return_sequences: int = 1,
                max_length: int = 512) -> List[Dict]:
        """Generate test cases"""
        input_text = self.format_input(feature_description, feature_type, test_type, domain)
        
        # Tokenize input
        inputs = self.tokenizer(input_text, return_tensors="pt", max_length=512, truncation=True)
        inputs = inputs.to(self.device)
        
        # Generate outputs
        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            num_return_sequences=num_return_sequences,
            num_beams=4,
            no_repeat_ngram_size=2,
            temperature=0.7,
            do_sample=True,
            top_k=50,
            top_p=0.95,
            early_stopping=True
        )
        
        # Decode and format outputs
        decoded_outputs = [self.tokenizer.decode(output, skip_special_tokens=False) for output in outputs]
        return [self.format_output(output) for output in decoded_outputs]

    def train_step(self, batch: Dict[str, torch.Tensor]) -> Dict[str, float]:
        """Single training step"""
        self.model.train()
        outputs = self.model(
            input_ids=batch["input_ids"].to(self.device),
            attention_mask=batch["attention_mask"].to(self.device),
            labels=batch["labels"].to(self.device)
        )
        
        return {
            "loss": outputs.loss.item(),
            "logits": outputs.logits
        }

    def save_model(self, path: str):
        """Save the model and tokenizer"""
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)

    def load_model(self, path: str):
        """Load the model and tokenizer"""
        self.model = T5ForConditionalGeneration.from_pretrained(path).to(self.device)
        self.tokenizer = T5Tokenizer.from_pretrained(path)

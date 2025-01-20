# GreenOak Test Case Generator 🌳

A trainable AI model for generating domain-specific test cases with comprehensive analytics and visualizations.

## 🌟 Features

- 🧠 **Trainable Model**: Fine-tune the model on your organization's test cases
- 🎯 **Domain-Specific Generation**: Specialized test cases for different industries
- 📊 **Analytics Dashboard**: Track and visualize model performance
- 🔄 **Continuous Learning**: Improve with feedback and new data
- 📈 **Performance Metrics**: Monitor precision, recall, and F1 scores
- 🎨 **Interactive UI**: User-friendly Streamlit interface
- 📝 **Multiple Export Formats**: JSON and Markdown support

## 🏗️ Architecture

The project uses a T5-based transformer model with the following components:

1. **Core Model** (`model.py`):
   - T5 transformer for sequence-to-sequence learning
   - Custom tokenization with domain-specific tokens
   - Structured output generation

2. **Training Pipeline** (`trainer.py`):
   - Custom training loop with validation
   - Learning rate scheduling
   - Checkpoint management
   - Performance visualization

3. **Data Management** (`dataset.py`):
   - Custom dataset implementation
   - Data preprocessing and augmentation
   - Efficient batching

4. **Web Interface** (`app.py`):
   - Streamlit-based UI
   - Real-time generation
   - Analytics dashboard
   - History tracking

## 📊 Model Performance

The model's performance is tracked through various metrics:

- Training and validation loss curves
- Precision, recall, and F1 scores
- Learning rate schedules
- Generation quality metrics
- Domain-specific accuracy

## 🚀 Getting Started

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Train the model:
```bash
python -m src.train \
    --train_data data/train.json \
    --val_data data/val.json \
    --output_dir models/
```

3. Run the web interface:
```bash
python -m src.train \
    --train_data data/train.json \
    --val_data data/val.json \
    --output_dir models/
```

## 📝 Data Format

Training data should be in JSON format:
```json
{
    "feature_description": "User login functionality",
    "feature_type": "UI",
    "test_type": "End-to-End Testing",
    "domain": "Fintech",
    "scenario": "Verify user login with valid credentials",
    "steps": ["Enter username", "Enter password", "Click login"],
    "expected_results": ["User successfully logged in"],
    "test_data": {
        "username": "test@example.com",
        "password": "validPassword123"
    },
    "requirements": ["2FA enabled", "Password complexity rules"]
}
```

## 📈 Analytics

The system provides comprehensive analytics:

- Model performance metrics
- Usage statistics by domain
- Test case distribution
- Generation history
- Quality metrics

## 🔧 Customization

1. **Domain Templates**: Add new domains in `model.py`
2. **Training Parameters**: Adjust in `trainer.py`
3. **UI Components**: Modify `app.py`
4. **Data Processing**: Customize `dataset.py`

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

MIT License - feel free to use and modify!

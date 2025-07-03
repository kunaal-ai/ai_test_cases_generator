# Garuda Test Case Generator - AI Agent


> Transform feature descriptions into comprehensive test scenarios with AI-powered intelligence

Garuda is an innovative test case generator that leverages OpenAI's GPT-4 to create detailed, context-aware test scenarios and test data. Whether you're testing UI components, APIs, databases, mobile apps, or complex integrations, Garuda helps you generate thorough test cases with just a few clicks.



## ✨ Features

- **Smart Test Generation**: Creates detailed test scenarios based on feature descriptions
- **Multiple Testing Types**: Supports Smoke, End-to-End, Performance, Regression, Security, and Accessibility testing
- **Comprehensive Coverage**: Generates test cases for UI, API, Database, Mobile, and Integration features
- **Domain-Specific Testing**: Specialized test cases for Fintech, Healthcare, E-commerce, Manufacturing, and Education
- **Test Data Generation**: Creates realistic test data, mock data, and environment setups
- **Beautiful UI**: Streamlit-based interface for easy interaction
- **Multiple Export Formats**: Download test cases in both Markdown and JSON formats
- **Flexible API Key Management**: Use environment variables or UI input for API key


## 🚀 Getting Started

### Prerequisites

- Python 3.8 or higher
- OpenAI API key
- pip (Python package manager)

### Installation

**Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai_test_cases_generator.git
   cd ai_test_cases_generator

   # create venv
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate

   # install dependencies
   pip install -r requirements.txt

   # Key
   Edit .env and add your OpenAI API key OR on UI field
   ```

### 🎮 Usage

1. **Start the application**
   ```bash
   streamlit run garuda.py
   ```

2. **Export Results**
   - View generated test cases in the UI
   - Download as Markdown for documentation
   - Download as JSON for automation

## Test Types
Smoke, End-to-End, Performance, Regression, Security, Accessibility


## Feature Types
 UI, API, Database, Mobile, Integration, Domain-Specific Testing

## Domains
Fintech, Healthcare, E-commerce, Manufacturing, Education


## 📝 Generated Test Data

For each test case, Garuda can generate:

- **Test Inputs**: Valid/invalid values, edge cases
- **Test Payloads**: Request/response examples
- **Mock Data**: External service responses
- **Environment Setup**: Required configurations

## 🙏 Acknowledgments

- OpenAI for the powerful GPT-4 API
- Streamlit for the amazing UI framework
- The testing community for inspiration

---

Made with ❤️ by Kunaal Thanik

*Remember: The best tests are those that find bugs before users do!* 🐛✨

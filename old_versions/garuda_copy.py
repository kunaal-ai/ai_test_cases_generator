import streamlit as st
import json
from openai import OpenAI
from typing import Dict
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
class TestCaseGenerator:
    def __init__(self, api_key: str):
        """Initialize the generator with OpenAI API key"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    
    def generate_test_scenarios(self, feature_description: str, feature_type: str, test_type: str) -> Dict:
        """Generate test scenarios based on feature description, feature type, and test type"""
        
        # Feature type specific considerations
        feature_templates = {
            "UI": """
            Additional considerations for UI testing:
            1. Cross-browser compatibility
            2. Responsive design for different screen sizes
            3. UI element positioning and styling
            4. Accessibility requirements
            5. Input field validations
            """,
            "API": """
            Additional considerations for API testing:
            1. Different HTTP methods (GET, POST, PUT, DELETE)
            2. Request/Response payload validation
            3. Status codes and error responses
            4. API authentication and authorization
            5. Rate limiting and performance
            """,
            "Database": """
            Additional considerations for Database testing:
            1. Data CRUD operations
            2. Data integrity and consistency
            3. Database transactions and rollbacks
            4. Performance and indexing
            5. Data backup and recovery
            """
        }

        # Test type specific considerations
        test_templates = {
            "Smoke Testing": """
            Focus on critical path testing:
            1. Core functionality verification
            2. Basic navigation flows
            3. Critical business transactions
            4. Basic data operations
            5. Essential integrations
            Aim for quick verification of fundamental features.
            """,
            "End-to-End Testing": """
            Focus on complete business flows:
            1. Full user journeys
            2. Integration between all components
            3. Data flow across systems
            4. Third-party integrations
            5. Real-world usage scenarios
            Cover entire system workflow from start to finish.
            """,
            "Performance Testing": """
            Focus on system performance:
            1. Response time benchmarks
            2. Load testing scenarios
            3. Stress testing conditions
            4. Scalability verification
            5. Resource utilization
            Include specific performance metrics and thresholds.
            """,
            "Regression Testing": """
            Focus on impact analysis:
            1. Existing functionality verification
            2. Integration points
            3. Common user flows
            4. Historical defect areas
            5. Configuration testing
            Ensure no existing features are broken.
            """,
            "Security Testing": """
            Focus on security aspects:
            1. Authentication mechanisms
            2. Authorization levels
            3. Data encryption
            4. Input validation
            5. Security vulnerabilities
            Include common security threats and preventions.
            """
        }

        prompt = f"""
        Feature Description:
        {feature_description}

        {feature_templates.get(feature_type, "")}
        
        {test_templates.get(test_type, "")}

        Please generate comprehensive test scenarios and test cases specifically for {test_type} in the following JSON format:
        {{
            "feature_name": "Name of the feature",
            "test_type": "{test_type}",
            "scenarios": [
                {{
                    "scenario_name": "Name of the scenario",
                    "description": "Description of the scenario",
                    "test_cases": [
                        {{
                            "id": "TC_001",
                            "title": "Test case title",
                            "preconditions": ["List of preconditions"],
                            "steps": ["Step 1", "Step 2"],
                            "expected_results": ["Expected result 1", "Expected result 2"],
                            "type": "Positive/Negative",
                            "priority": "High/Medium/Low"
                        }}
                    ]
                }}
            ]
        }}
        """

        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a QA expert who creates detailed test scenarios and test cases."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )

        return json.loads(response.choices[0].message.content)

    # format_as_markdown method remains the same
    def format_as_markdown(self, test_data: Dict) -> str:
        """Convert the test scenarios and cases to markdown format"""
        markdown = f"# Test Scenarios for {test_data['feature_name']}\n"
        markdown += f"## Test Type: {test_data['test_type']}\n\n"
        
        for scenario in test_data['scenarios']:
            markdown += f"## {scenario['scenario_name']}\n"
            markdown += f"{scenario['description']}\n\n"
            
            for test_case in scenario['test_cases']:
                markdown += f"### {test_case['id']}: {test_case['title']}\n"
                markdown += f"**Priority:** {test_case['priority']}\n"
                markdown += f"**Type:** {test_case['type']}\n\n"
                
                markdown += "**Preconditions:**\n"
                for pre in test_case['preconditions']:
                    markdown += f"- {pre}\n"
                
                markdown += "\n**Steps:**\n"
                for i, step in enumerate(test_case['steps'], 1):
                    markdown += f"{i}. {step}\n"
                
                markdown += "\n**Expected Results:**\n"
                for result in test_case['expected_results']:
                    markdown += f"- {result}\n"
                
                markdown += "\n---\n"
        
        return markdown

def main():
    st.set_page_config(page_title="Test Case Generator", page_icon="🧪")
    
    st.title("Test Case Generator")
    st.write("Generate test scenarios and cases from feature descriptions")

    # Sidebar for API key
    with st.sidebar:
        st.header("Settings")
        api_key = st.text_input("Enter OpenAI API Key", type="password")
        st.markdown("""
        ### How to use:
        1. Enter your OpenAI API key
        2. Select feature type
        3. Select test type
        4. Enter feature description
        5. Click Generate
        6. Download results
        """)

    # Main interface
    col1, col2 = st.columns(2)
    
    with col1:
        feature_type = st.selectbox(
            "Select Feature Type",
            ["UI", "API", "Database"]
        )
    
    with col2:
        test_type = st.selectbox(
            "Select Test Type",
            ["Smoke Testing", "End-to-End Testing", "Performance Testing", 
             "Regression Testing", "Security Testing"]
        )

    feature_description = st.text_area(
        "Enter Feature Description",
        height=200,
        placeholder="Describe the feature you want to generate test cases for..."
    )

    if st.button("Generate Test Cases"):
        if not api_key:
            st.error("Please enter your OpenAI API key in the sidebar")
            return
        
        if not feature_description:
            st.error("Please enter a feature description")
            return

        try:
            with st.spinner("Generating test cases..."):
                generator = TestCaseGenerator(api_key)
                test_data = generator.generate_test_scenarios(feature_description, feature_type, test_type)
                markdown_output = generator.format_as_markdown(test_data)

                # Display results
                st.markdown(markdown_output)

                # Download buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    st.download_button(
                        label="Download as Markdown",
                        data=markdown_output,
                        file_name="test_scenarios.md",
                        mime="text/markdown"
                    )
                
                with col2:
                    st.download_button(
                        label="Download as JSON",
                        data=json.dumps(test_data, indent=2),
                        file_name="test_scenarios.json",
                        mime="application/json"
                    )

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
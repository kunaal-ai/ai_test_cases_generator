import streamlit as st
import json
from typing import Dict
import os
from dotenv import load_dotenv
from openai import OpenAI
from templates import DOMAIN_TEMPLATES, FEATURE_TEMPLATES, TEST_TEMPLATES

# Load environment variables from .env file
load_dotenv()

class TestCaseGenerator:
    def __init__(self, api_key: str = None):
        """Initialize the generator with OpenAI API key"""
        # Try to get API key from parameter first, then from environment variable
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        
        if not self.api_key or not self.api_key.strip():
            raise ValueError("API key must be provided either through parameter or OPENAI_API_KEY environment variable")
        
        self.client = OpenAI(api_key=self.api_key)
        
        # Initialize all templates from the templates module
        self.domain_templates = DOMAIN_TEMPLATES
        self.feature_templates = FEATURE_TEMPLATES
        self.test_templates = TEST_TEMPLATES

    def generate_test_scenarios(self, feature_description: str, feature_type: str, test_type: str, domain: str = None, generate_test_data: bool = False) -> Dict:
        """Generate test scenarios based on feature description, feature type, and test type"""
        
        # Get domain-specific template if domain is specified
        domain_template = ""
        if domain and domain in self.domain_templates:
            domain_template = f"""
            Domain-Specific Considerations:
            {self.domain_templates[domain]}
            """
        
        # Use instance variables for templates

        prompt = f"""
        Feature Description:
        {feature_description}

        {domain_template}
        
        {self.feature_templates.get(feature_type, '')}
        
        {self.test_templates.get(test_type, '')}

        Please generate comprehensive test scenarios and test cases specifically for {test_type} in the following JSON format:
        {{
            "feature_name": "Name of the feature",
            "test_type": "{test_type}",
            "feature_type": "{feature_type}",
            "domain": "{domain if domain else 'General'}",
            "scenarios": [
                {{
                    "scenario_name": "Name of the scenario",
                    "description": "Description of the scenario",
                    "domain_specific_requirements": ["List of domain-specific requirements"],
                    "prerequisites": ["List of prerequisites"],
                    "test_cases": [
                        {{
                            "id": "TC_001",
                            "title": "Test case title",
                            "description": "Detailed description of the test case",
                            "preconditions": ["List of preconditions"],
                            "dependencies": ["List of dependencies"],
                            "steps": ["Step 1", "Step 2"],
                            "expected_results": ["Expected result 1", "Expected result 2"],
                            "type": "Positive/Negative",
                            "priority": "High/Medium/Low",
                            "severity": "Critical/Major/Minor",
                            "domain_considerations": ["List of domain-specific considerations"],
                            "compliance_requirements": ["List of compliance requirements"],
                            "test_data": {{
                                "inputs": ["Sample input data"],
                                "validation_rules": ["Data validation rules"],
                                "edge_cases": ["Edge case scenarios"],
                                "domain_specific_data": ["Domain-specific test data"]
                            }},
                            "environment": {{
                                "requirements": ["Environment requirements"],
                                "configuration": ["Configuration settings"],
                                "domain_specific_setup": ["Domain-specific setup requirements"]
                            }},
                            "tags": ["List of relevant tags"]
                        }}
                    ]
                }}
            ]
        }}

        Please ensure to include domain-specific:
        1. Compliance requirements
        2. Security considerations
        3. Integration points
        4. Data validation rules
        5. Test data examples
        6. Environmental setup
        7. Edge cases specific to the domain
        8. Industry standard practices
        9. Common failure scenarios
        10. Performance requirements
        """

        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a QA expert who creates detailed test scenarios and test cases with focus on edge cases, security, performance, and accessibility."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            test_scenarios = json.loads(response.choices[0].message.content)
            
            # Generate test data if requested
            if generate_test_data:
                for scenario in test_scenarios['scenarios']:
                    for test_case in scenario['test_cases']:
                        test_case['generated_test_data'] = self.generate_test_data(test_case, feature_type)
            
            return test_scenarios
            
        except Exception as e:
            raise Exception(f"Failed to generate test scenarios: {str(e)}")

    def generate_test_data(self, test_case: Dict, feature_type: str) -> Dict:
        """Generate relevant test data for a test case based on its type and requirements"""
        
        prompt = f"""
        Given the following test case details, generate realistic and comprehensive test data:

        Test Case: {test_case['title']}
        Description: {test_case.get('description', '')}
        Type: {test_case['type']}
        Feature Type: {feature_type}

        Requirements:
        1. Preconditions: {', '.join(test_case['preconditions'])}
        2. Steps: {', '.join(test_case['steps'])}
        3. Expected Results: {', '.join(test_case['expected_results'])}

        IMPORTANT: Your response must be a valid JSON object that follows this exact structure:
        {{
            "test_inputs": [
                {{
                    "name": "Input field/parameter name",
                    "description": "Description of the input",
                    "data_type": "string/number/boolean/array/object",
                    "valid_values": ["List of valid test values"],
                    "invalid_values": ["List of invalid test values"],
                    "edge_cases": ["List of edge case values"],
                    "constraints": ["List of constraints"]
                }}
            ],
            "test_payloads": [
                {{
                    "scenario": "Scenario name (e.g., Valid case, Invalid case, Edge case)",
                    "description": "Description of the test payload",
                    "payload": {{
                        "field1": "value1",
                        "field2": "value2"
                    }},
                    "expected_response": {{
                        "status": "success/error",
                        "data": "Expected response data"
                    }}
                }}
            ],
            "mock_data": [
                {{
                    "type": "Type of mock (e.g., Database record, API response)",
                    "description": "Description of the mock data",
                    "data": "Mock data in appropriate format"
                }}
            ],
            "environment_setup": {{
                "database": ["Required database state/records"],
                "files": ["Required files/file content"],
                "configurations": ["Required configuration settings"],
                "external_services": ["Required external service states"]
            }}
        }}

        Consider the following based on feature type:
        1. For UI: Include form data, validation rules, file uploads
        2. For API: Include request/response payloads, headers, query params
        3. For Database: Include database records, relationships, constraints
        4. For Mobile: Include device-specific data, offline data
        5. For Integration: Include mock service responses, event payloads

        Ensure to include:
        1. Both valid and invalid test data
        2. Edge cases and boundary values
        3. Special characters and formats
        4. Different data types
        5. Required mock data
        6. Environmental setup data
        """

        try:
            # First, try to get the model from environment variable or use gpt-4 as default
            model = os.getenv('OPENAI_MODEL', 'gpt-4')
            
            # Update the prompt to be more explicit about the JSON format
            json_prompt = f"""You must respond with a valid JSON object that follows this exact structure:
            {json.dumps({
                "test_inputs": [{"name": "", "description": "", "data_type": "", "valid_values": [], "invalid_values": [], "edge_cases": [], "constraints": []}],
                "test_payloads": [{"scenario": "", "description": "", "payload": {}, "expected_response": {}}],
                "mock_data": [{"type": "", "description": "", "data": {}}],
                "environment_setup": {"database": [], "files": [], "configurations": [], "external_services": []}
            }, indent=2)}
            
            {prompt}
            
            Respond with ONLY the JSON object, without any markdown formatting or additional text."""
            
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a QA expert who creates comprehensive and realistic test data. You must respond with a valid JSON object that matches the required structure exactly."},
                    {"role": "user", "content": json_prompt}
                ],
                temperature=0.7
            )
            
            # Get the response content
            response_content = response.choices[0].message.content.strip()
            
            # Clean the response to extract JSON if it's wrapped in markdown code blocks
            if '```json' in response_content:
                response_content = response_content.split('```json')[1].split('```')[0].strip()
            elif '```' in response_content:
                response_content = response_content.split('```')[1].split('```')[0].strip()
                
            # Parse the JSON with better error handling
            try:
                return json.loads(response_content)
            except json.JSONDecodeError as e:
                # Try to extract JSON from the response
                try:
                    # Look for JSON object in the response
                    import re
                    json_match = re.search(r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}', response_content)
                    if json_match:
                        return json.loads(json_match.group(0))
                    else:
                        # Try to clean up common formatting issues
                        cleaned = re.sub(r'^[^{]*', '', response_content)  # Remove everything before first {
                        cleaned = re.sub(r'[^}]*$', '', cleaned)  # Remove everything after last }
                        if cleaned:
                            return json.loads(cleaned)
                        raise Exception("No valid JSON object found in response")
                except Exception as inner_e:
                    # If we still can't parse, provide a helpful error message
                    error_msg = f"""
                    Failed to parse JSON response. Please ensure the response is valid JSON.
                    
                    Error: {str(inner_e)}
                    
                    Response content was:
                    {response_content}
                    """
                    raise Exception(error_msg) from None
                
        except Exception as e:
            raise Exception(f"Failed to generate test data: {str(e)}")

    def format_as_markdown(self, test_data: Dict) -> str:
        """Convert the test scenarios and cases to markdown format"""
        markdown = f"# Test Scenarios for {test_data['feature_name']}\n"
        markdown += f"## Test Type: {test_data['test_type']}\n"
        markdown += f"## Feature Type: {test_data['feature_type']}\n"
        markdown += f"## Domain: {test_data['domain']}\n\n"
        
        for scenario in test_data['scenarios']:
            markdown += f"## {scenario['scenario_name']}\n"
            markdown += f"{scenario['description']}\n\n"
            
            markdown += "### Prerequisites:\n"
            for prereq in scenario.get('prerequisites', []):
                markdown += f"- {prereq}\n\n"
            
            for test_case in scenario['test_cases']:
                markdown += f"### {test_case['id']}: {test_case['title']}\n"
                markdown += f"**Description:** {test_case.get('description', '')}\n"
                markdown += f"**Priority:** {test_case['priority']}\n"
                markdown += f"**Severity:** {test_case.get('severity', 'N/A')}\n"
                markdown += f"**Type:** {test_case['type']}\n\n"
                
                if test_case.get('dependencies'):
                    markdown += "**Dependencies:**\n"
                    for dep in test_case['dependencies']:
                        markdown += f"- {dep}\n"
                    markdown += "\n"
                
                markdown += "**Preconditions:**\n"
                for pre in test_case['preconditions']:
                    markdown += f"- {pre}\n"
                
                markdown += "\n**Steps:**\n"
                for i, step in enumerate(test_case['steps'], 1):
                    markdown += f"{i}. {step}\n"
                
                markdown += "\n**Expected Results:**\n"
                for result in test_case['expected_results']:
                    markdown += f"- {result}\n"
                
                if test_case.get('generated_test_data'):
                    markdown += "\n**Generated Test Data:**\n"
                    
                    markdown += "\n*Test Inputs:*\n"
                    for input_data in test_case['generated_test_data'].get('test_inputs', []):
                        markdown += f"* {input_data['name']} ({input_data['data_type']}):\n"
                        markdown += f"  - Description: {input_data['description']}\n"
                        markdown += f"  - Valid Values: {', '.join(input_data['valid_values'])}\n"
                        markdown += f"  - Invalid Values: {', '.join(input_data['invalid_values'])}\n"
                        markdown += f"  - Edge Cases: {', '.join(input_data['edge_cases'])}\n"
                        markdown += f"  - Constraints: {', '.join(input_data['constraints'])}\n\n"
                    
                    markdown += "\n*Test Payloads:*\n"
                    for payload in test_case['generated_test_data'].get('test_payloads', []):
                        markdown += f"* {payload['scenario']}:\n"
                        markdown += f"  - Description: {payload['description']}\n"
                        markdown += f"  - Payload: ```json\n{json.dumps(payload['payload'], indent=2)}```\n"
                        markdown += f"  - Expected Response: ```json\n{json.dumps(payload['expected_response'], indent=2)}```\n\n"
                    
                    markdown += "\n*Mock Data:*\n"
                    for mock in test_case['generated_test_data'].get('mock_data', []):
                        markdown += f"* {mock['type']}:\n"
                        markdown += f"  - Description: {mock['description']}\n"
                        markdown += f"  - Data: ```json\n{json.dumps(mock['data'], indent=2)}```\n\n"
                    
                    markdown += "\n*Environment Setup:*\n"
                    env_setup = test_case['generated_test_data'].get('environment_setup', {})
                    for key, values in env_setup.items():
                        markdown += f"* {key.title()}:\n"
                        for value in values:
                            markdown += f"  - {value}\n"
                    markdown += "\n"
                
                if test_case.get('tags'):
                    markdown += "\n**Tags:** " + ", ".join(test_case['tags']) + "\n"
                
                markdown += "\n---\n"
        
        return markdown

def main():
    st.set_page_config(page_title="Test Case Generator", page_icon="🧪")
    
    st.title("Test Case Generator")
    st.write("Generate test scenarios and cases from feature descriptions")

    # Sidebar for API key and settings
    with st.sidebar:
        st.header("Settings")
        
        # Check if API key is in environment variables
        env_api_key = os.getenv('OPENAI_API_KEY')
        if env_api_key:
            st.success("API Key found in environment variables")
            use_env_key = st.checkbox("Use API Key from environment", value=True)
            if use_env_key:
                api_key = env_api_key
            else:
                api_key = st.text_input("Enter OpenAI API Key", type="password")
        else:
            st.info("No API Key found in environment variables")
            api_key = st.text_input("Enter OpenAI API Key", type="password")
        
        st.markdown("""
        ### How to use:
        1. Enter OpenAI API Key in textbox or set in .env file
        2. Select domain (optional)
        3. Select feature type
        4. Select test type
        5. Choose whether to generate test data
        6. Enter feature description
        7. Click Generate
        8. Download results
        
        Note: You can store your API key in a .env file to avoid entering it each time.
        Create a .env file in the project root and add:
        ```
        OPENAI_API_KEY=your_api_key_here
        ```
        """)

    # Main interface
    col1, col2, col3 = st.columns(3)
    
    with col1:
        domain = st.selectbox(
            "Select Domain (Optional)",
            ["General", "Fintech", "Healthcare", "E-commerce", "Manufacturing", "Education"],
            help="Choose a specific domain to generate domain-specific test cases"
        )
    
    with col2:
        feature_type = st.selectbox(
            "Select Feature Type",
            ["UI", "API", "Database", "Mobile", "Integration"]
        )
    
    with col3:
        test_type = st.selectbox(
            "Select Test Type",
            ["Smoke Testing", "End-to-End Testing", "Performance Testing", 
             "Regression Testing", "Security Testing", "Accessibility Testing"]
        )

    generate_test_data = st.checkbox("Generate Test Data", value=False, 
                                   help="Enable this to generate comprehensive test data for each test case")

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
            with st.spinner("Generating test cases..." + (" and test data..." if generate_test_data else "")):
                generator = TestCaseGenerator(api_key)
                test_data = generator.generate_test_scenarios(
                    feature_description, 
                    feature_type, 
                    test_type,
                    domain if domain != "General" else None,
                    generate_test_data
                )
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
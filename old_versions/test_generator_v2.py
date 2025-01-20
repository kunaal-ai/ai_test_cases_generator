import streamlit as st
import json
from openai import OpenAI
from typing import Dict

class TestCaseGenerator:
    def __init__(self, api_key: str):
        """Initialize the generator with OpenAI API key"""
        self.client = OpenAI(api_key="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")
    
    def generate_test_scenarios(self, feature_description: str, feature_type: str) -> Dict:
        """Generate test scenarios based on feature description and type"""
        
        # Template selection based on feature type
        template_additions = {
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

        prompt = f"""
        Feature Description:
        {feature_description}

        {template_additions.get(feature_type, "")}

        Please generate comprehensive test scenarios and test cases in the following JSON format:
        {{
            "feature_name": "Name of the feature",
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
        
        Consider:
        1. Both positive and negative test scenarios
        2. Edge cases and boundary conditions
        3. Different user roles and permissions
        4. Performance considerations
        5. Error handling scenarios
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

    def format_as_markdown(self, test_data: Dict) -> str:
        """Convert the test scenarios and cases to markdown format"""
        markdown = f"# Test Scenarios for {test_data['feature_name']}\n\n"
        
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
        3. Enter feature description
        4. Click Generate
        5. Download results
        """)

    # Main interface
    feature_type = st.selectbox(
        "Select Feature Type",
        ["UI", "API", "Database"]
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
                test_data = generator.generate_test_scenarios(feature_description, feature_type)
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
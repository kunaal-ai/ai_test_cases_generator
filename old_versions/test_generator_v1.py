from openai import OpenAI
from typing import List, Dict
import json
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()
class TestCaseGenerator:
    def __init__(self, api_key: str):
        """Initialize the generator with OpenAI API key"""
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate_test_scenarios(self, feature_description: str) -> Dict:
        """
        Generate test scenarios and test cases from feature description
        
        Parameters:
        feature_description: Detailed description of the feature
        
        Returns:
        Dictionary containing test scenarios and cases
        """
        prompt = f"""
        Feature Description:
        {feature_description}

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

    # Rest of the class remains the same...
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

# Example usage
if __name__ == "__main__":
    # Example feature description
    feature_desc = """
    User Login Feature:
    Users should be able to log in to the application using their email and password.
    The system should validate credentials, handle incorrect attempts, and support
    password recovery. After 3 failed attempts, the account should be temporarily
    locked for 30 minutes.
    """
    
    # Initialize generator with your API key
    generator = TestCaseGenerator("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")
    
    # Generate test scenarios and cases
    test_data = generator.generate_test_scenarios(feature_desc)
    
    # Convert to markdown
    markdown_output = generator.format_as_markdown(test_data)
    
    # Save to file
    with open("test_scenarios.md", "w") as f:
        f.write(markdown_output)

    print("✅ Test generation success ")
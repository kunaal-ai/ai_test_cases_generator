import streamlit as st
import json
from openai import OpenAI
from typing import Dict
import os
from dotenv import load_dotenv

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
        
        # Domain-specific templates
        self.domain_templates = {
            "Fintech": """
            Additional considerations for Fintech testing:
            1. Financial Regulations and Compliance:
                - KYC/AML requirements
                - Financial data security standards
                - Transaction reporting requirements
                - Regional regulatory compliance
                - Audit trail requirements
            
            2. Transaction Processing:
                - Payment processing accuracy
                - Currency conversion
                - Fee calculations
                - Transaction limits
                - Multi-currency support
            
            3. Security and Fraud:
                - Fraud detection mechanisms
                - Transaction monitoring
                - Account security measures
                - Authentication protocols
                - Financial data encryption
            
            4. Integration Testing:
                - Payment gateway integration
                - Banking system interfaces
                - Credit scoring systems
                - Financial data providers
                - Regulatory reporting systems
            
            5. Data Accuracy:
                - Financial calculations
                - Interest computations
                - Balance tracking
                - Transaction history
                - Statement generation
            """,
            
            "Healthcare": """
            Additional considerations for Healthcare testing:
            1. Regulatory Compliance:
                - HIPAA compliance
                - FDA regulations
                - Clinical data protection
                - Patient privacy
                - Medical device standards
            
            2. Patient Data Management:
                - Electronic Health Records (EHR)
                - Patient identification
                - Medical history tracking
                - Prescription management
                - Appointment scheduling
            
            3. Clinical Workflows:
                - Patient care protocols
                - Medical device integration
                - Lab result processing
                - Diagnostic procedures
                - Treatment planning
            
            4. Security and Privacy:
                - PHI protection
                - Access control
                - Audit logging
                - Data encryption
                - Consent management
            
            5. Integration Testing:
                - Medical device integration
                - Lab system interfaces
                - Pharmacy systems
                - Insurance verification
                - Healthcare provider networks
            """,
            
            "E-commerce": """
            Additional considerations for E-commerce testing:
            1. Shopping Experience:
                - Product catalog management
                - Search and filtering
                - Shopping cart functionality
                - Checkout process
                - Order tracking
            
            2. Payment Processing:
                - Multiple payment methods
                - Payment gateway integration
                - Refund processing
                - Invoice generation
                - Tax calculations
            
            3. Inventory Management:
                - Stock tracking
                - Product variants
                - Warehouse management
                - Supply chain integration
                - Inventory alerts
            
            4. Customer Management:
                - User accounts
                - Wishlist functionality
                - Order history
                - Customer support
                - Reviews and ratings
            
            5. Security:
                - Payment security
                - Customer data protection
                - Fraud prevention
                - PCI compliance
                - Session management
            """,
            
            "Manufacturing": """
            Additional considerations for Manufacturing testing:
            1. Production Systems:
                - Manufacturing process control
                - Quality control systems
                - Equipment monitoring
                - Production scheduling
                - Resource management
            
            2. Supply Chain:
                - Inventory tracking
                - Supplier management
                - Material requirements planning
                - Warehouse operations
                - Shipping logistics
            
            3. Quality Assurance:
                - Product specifications
                - Quality metrics
                - Compliance tracking
                - Defect management
                - Inspection procedures
            
            4. Equipment Integration:
                - Machine control systems
                - Sensor data processing
                - Maintenance scheduling
                - Performance monitoring
                - Alert systems
            
            5. Regulatory Compliance:
                - Safety standards
                - Environmental regulations
                - Industry certifications
                - Documentation requirements
                - Audit trail
            """,
            
            "Education": """
            Additional considerations for Education testing:
            1. Learning Management:
                - Course management
                - Content delivery
                - Student progress tracking
                - Assessment systems
                - Grading functionality
            
            2. User Management:
                - Student profiles
                - Teacher accounts
                - Parent access
                - Administrative roles
                - Class management
            
            3. Content Delivery:
                - Multimedia support
                - Interactive content
                - Assignment submission
                - Resource management
                - Accessibility compliance
            
            4. Assessment:
                - Quiz/Test creation
                - Automated grading
                - Progress reports
                - Performance analytics
                - Feedback systems
            
            5. Communication:
                - Messaging systems
                - Discussion forums
                - Announcement broadcasts
                - Parent communication
                - Calendar integration
            """
        }

    def generate_test_scenarios(self, feature_description: str, feature_type: str, test_type: str, domain: str = None, generate_test_data: bool = False) -> Dict:
        """Generate test scenarios based on feature description, feature type, and test type"""
        
        # Get domain-specific template if domain is specified
        domain_template = ""
        if domain and domain in self.domain_templates:
            domain_template = f"""
            Domain-Specific Considerations:
            {self.domain_templates[domain]}
            """
        
        # Feature type specific considerations
        feature_templates = {
            "UI": """
            Additional considerations for UI testing:
            1. Cross-browser compatibility (Chrome, Firefox, Safari, Edge)
            2. Responsive design (Mobile, Tablet, Desktop, Ultra-wide screens)
            3. UI element states (Enabled, Disabled, Hover, Focus, Active)
            4. Accessibility (WCAG compliance, Screen readers, Keyboard navigation)
            5. Input field validations (Boundary values, Special characters, XSS prevention)
            6. Layout and styling (RTL support, Dark/Light themes, Font scaling)
            7. Error states and messages
            8. Loading states and animations
            9. Browser storage handling
            10. Offline functionality
            """,
            "API": """
            Additional considerations for API testing:
            1. HTTP methods (GET, POST, PUT, PATCH, DELETE, OPTIONS)
            2. Request/Response validation (Headers, Body, Query params, Path params)
            3. Status codes (Success, Client errors, Server errors)
            4. Authentication (Basic, Bearer, OAuth, API keys)
            5. Authorization (Role-based access, Permissions)
            6. Rate limiting and throttling
            7. Request timeouts and retries
            8. API versioning
            9. Payload size limits
            10. CORS and security headers
            """,
            "Database": """
            Additional considerations for Database testing:
            1. CRUD operations with edge cases
            2. Data integrity (Constraints, Triggers, Cascading)
            3. Transaction management (Commit, Rollback, Deadlocks)
            4. Concurrent access and race conditions
            5. Data migration and versioning
            6. Backup and recovery scenarios
            7. Performance optimization (Indexing, Query plans)
            8. Data encryption and security
            9. Connection pooling and timeouts
            10. Data archival and cleanup
            """,
            "Mobile": """
            Additional considerations for Mobile testing:
            1. Platform specific behavior (iOS, Android)
            2. Device fragmentation (Screen sizes, OS versions)
            3. Network conditions (2G, 3G, 4G, 5G, Offline)
            4. Battery consumption and performance
            5. App lifecycle (Background, Foreground, Killed)
            6. Device permissions and settings
            7. Push notifications
            8. Local storage and caching
            9. App updates and migrations
            10. Integration with device features (Camera, GPS, Biometrics)
            """,
            "Integration": """
            Additional considerations for Integration testing:
            1. System dependencies and interfaces
            2. Data flow between components
            3. Error handling and recovery
            4. Service contracts and versioning
            5. Asynchronous operations
            6. Message queues and events
            7. External service mocking
            8. Configuration management
            9. Deployment scenarios
            10. Monitoring and logging
            """
        }

        # Test type specific considerations
        test_templates = {
            "Smoke Testing": """
            Focus on critical path testing:
            1. Core functionality verification
            2. Basic navigation flows
            3. Critical business transactions
            4. Essential integrations
            5. Basic error handling
            Include quick verification of fundamental features.
            """,
            "End-to-End Testing": """
            Focus on complete business flows:
            1. Full user journeys and scenarios
            2. Cross-component interactions
            3. Data flow across systems
            4. Third-party integrations
            5. Error scenarios and recovery
            6. Edge cases and boundary conditions
            7. Different user roles and permissions
            8. Configuration variations
            9. Performance implications
            10. Security considerations
            """,
            "Performance Testing": """
            Focus on system performance:
            1. Response time benchmarks
            2. Load testing scenarios (Normal, Peak, Stress)
            3. Scalability verification
            4. Resource utilization (CPU, Memory, Network, Disk)
            5. Concurrency and parallel processing
            6. Caching effectiveness
            7. Database performance
            8. Network latency impact
            9. Third-party service performance
            10. Recovery time objectives
            """,
            "Regression Testing": """
            Focus on impact analysis:
            1. Existing functionality verification
            2. Integration points
            3. Common user flows
            4. Historical defect areas
            5. Configuration testing
            6. Cross-browser compatibility
            7. Database migrations
            8. API versioning
            9. Security compliance
            10. Performance baselines
            """,
            "Security Testing": """
            Focus on security aspects:
            1. Authentication mechanisms
            2. Authorization and access control
            3. Data encryption (In-transit, At-rest)
            4. Input validation and sanitization
            5. Common vulnerabilities (OWASP Top 10)
            6. Session management
            7. API security
            8. File upload/download security
            9. Audit logging
            10. Compliance requirements
            """,
            "Accessibility Testing": """
            Focus on accessibility compliance:
            1. Screen reader compatibility
            2. Keyboard navigation
            3. Color contrast and visibility
            4. Alternative text for images
            5. ARIA labels and roles
            6. Focus management
            7. Form field accessibility
            8. Error message announcements
            9. Document structure
            10. Multimedia accessibility
            """
        }

        prompt = f"""
        Feature Description:
        {feature_description}

        {domain_template}
        
        {feature_templates.get(feature_type, "")}
        
        {test_templates.get(test_type, "")}

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

        Please generate test data in the following JSON format:
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
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are a QA expert who creates comprehensive and realistic test data."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )
            return json.loads(response.choices[0].message.content)
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
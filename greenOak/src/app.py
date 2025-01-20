import streamlit as st
import torch
from pathlib import Path
import json
from model import TestCaseGenerator
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
from typing import Dict, List
import torch

class TestCaseGeneratorApp:
    def __init__(self, model_path: str = "models/best"):
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = TestCaseGenerator(device=self.device)
        if Path(model_path).exists():
            self.model.load_model(model_path)
        
        # Initialize session state
        if 'history' not in st.session_state:
            st.session_state.history = []
        if 'metrics' not in st.session_state:
            st.session_state.metrics = {
                'generation_count': 0,
                'domains': {},
                'feature_types': {},
                'test_types': {}
            }

    def update_metrics(self, domain: str, feature_type: str, test_type: str):
        """Update usage metrics"""
        metrics = st.session_state.metrics
        metrics['generation_count'] += 1
        metrics['domains'][domain] = metrics['domains'].get(domain, 0) + 1
        metrics['feature_types'][feature_type] = metrics['feature_types'].get(feature_type, 0) + 1
        metrics['test_types'][test_type] = metrics['test_types'].get(test_type, 0) + 1

    def plot_metrics(self):
        """Generate metrics visualizations"""
        metrics = st.session_state.metrics
        
        st.subheader("Usage Analytics")
        col1, col2 = st.columns(2)
        
        with col1:
            # Domain distribution
            if metrics['domains']:
                fig_domains = px.pie(
                    names=list(metrics['domains'].keys()),
                    values=list(metrics['domains'].values()),
                    title="Test Cases by Domain"
                )
                st.plotly_chart(fig_domains)
            else:
                st.info("No domain data available yet")
        
        with col2:
            # Feature type distribution
            if metrics['feature_types']:
                df_features = pd.DataFrame({
                    'Feature Type': list(metrics['feature_types'].keys()),
                    'Count': list(metrics['feature_types'].values())
                })
                fig_features = px.bar(
                    df_features,
                    x='Feature Type',
                    y='Count',
                    title="Test Cases by Feature Type"
                )
                st.plotly_chart(fig_features)
            else:
                st.info("No feature type data available yet")
        
        # Test type trends
        if metrics['test_types']:
            df_test_types = pd.DataFrame({
                'Test Type': list(metrics['test_types'].keys()),
                'Count': list(metrics['test_types'].values())
            })
            fig_test_types = px.bar(
                df_test_types,
                x='Test Type',
                y='Count',
                title="Test Cases by Test Type"
            )
            st.plotly_chart(fig_test_types)
        else:
            st.info("No test type data available yet")

    def display_history(self):
        """Display generation history"""
        if st.session_state.history:
            st.subheader("Generation History")
            for item in reversed(st.session_state.history[-5:]):  # Show last 5 entries
                with st.expander(f"{item['domain']} - {item['feature_type']} - {item['test_type']}"):
                    st.json(item['test_cases'])

    def run(self):
        """Run the Streamlit app"""
        st.title("GreenOak Test Case Generator")
        st.write("Generate domain-specific test cases with our trained model")

        # Input form
        with st.form("test_case_form"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                domain = st.selectbox(
                    "Select Domain",
                    ["General", "Fintech", "Healthcare", "E-commerce", "Manufacturing", "Education"]
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

            feature_description = st.text_area(
                "Feature Description",
                height=100,
                placeholder="Describe the feature you want to test..."
            )

            num_test_cases = st.slider("Number of Test Cases", 1, 5, 1)
            
            submitted = st.form_submit_button("Generate Test Cases")

        if submitted and feature_description:
            with st.spinner("Generating test cases..."):
                # Generate test cases
                test_cases = self.model.generate(
                    feature_description=feature_description,
                    feature_type=feature_type,
                    test_type=test_type,
                    domain=domain if domain != "General" else None,
                    num_return_sequences=num_test_cases
                )

                # Update metrics
                self.update_metrics(domain, feature_type, test_type)
                
                # Add to history
                st.session_state.history.append({
                    'domain': domain,
                    'feature_type': feature_type,
                    'test_type': test_type,
                    'test_cases': test_cases
                })

                # Display results
                st.subheader("Generated Test Cases")
                for i, test_case in enumerate(test_cases, 1):
                    with st.expander(f"Test Case {i}"):
                        st.json(test_case)

                # Download options
                col1, col2 = st.columns(2)
                with col1:
                    st.download_button(
                        "Download as JSON",
                        data=json.dumps(test_cases, indent=2),
                        file_name="test_cases.json",
                        mime="application/json"
                    )
                with col2:
                    # Convert to markdown
                    markdown = "# Generated Test Cases\n\n"
                    for i, tc in enumerate(test_cases, 1):
                        markdown += f"## Test Case {i}\n"
                        markdown += f"### Scenario\n{tc['scenario']}\n\n"
                        markdown += "### Steps\n" + "\n".join(f"- {step}" for step in tc['steps']) + "\n\n"
                        markdown += "### Expected Results\n" + "\n".join(f"- {result}" for result in tc['expected_results']) + "\n\n"
                        markdown += "### Requirements\n" + "\n".join(f"- {req}" for req in tc['requirements']) + "\n\n"
                        markdown += f"### Test Data\n```json\n{json.dumps(tc['test_data'], indent=2)}\n```\n\n"
                    
                    st.download_button(
                        "Download as Markdown",
                        data=markdown,
                        file_name="test_cases.md",
                        mime="text/markdown"
                    )

        # Display metrics and history
        self.plot_metrics()
        self.display_history()

if __name__ == "__main__":
    app = TestCaseGeneratorApp()
    app.run()

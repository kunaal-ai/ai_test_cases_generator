import streamlit as st
import os
import json
import time
import re
import matplotlib.pyplot as plt
import pandas as pd
from typing import Dict, Any, Optional, List, Tuple
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

def execute_api_test(test_config: dict) -> dict:
    """Execute an API test using the requests library."""
    import requests
    
    start_time = time.time()
    result = {
        'success': False,
        'status': 'pending',
        'start_time': start_time,
        'request': {
            'method': test_config.get('method', 'GET'),
            'url': test_config.get('url'),
            'headers': test_config.get('headers', {}),
            'params': test_config.get('params', {})
        }
    }
    
    try:
        if not (url := test_config.get('url')):
            raise ValueError("URL is required for API test")
            
        # Make the request
        kwargs = {
            'method': test_config.get('method', 'GET').upper(),
            'url': url,
            'headers': test_config.get('headers', {}),
            'params': test_config.get('params', {})
        }
        
        if 'json' in test_config:
            kwargs['json'] = test_config['json']
            
        response = requests.request(**kwargs)
        duration = time.time() - start_time
        
        # Build response data
        response_data = {
            'status_code': response.status_code,
            'headers': dict(response.headers),
            'body': response.json() if response.content else None,
            'size': len(response.content) if response.content else 0
        }
        
        # Update result
        result.update({
            'end_time': start_time + duration,
            'duration': duration,
            'response': response_data,
            'metrics': {
                'response_time': duration * 1000,
                'latency': duration * 1000,
                'response_size': response_data['size'],
                'request_size': len(str(test_config.get('json', '')).encode('utf-8'))
            }
        })
        
        # Check expected status
        if (expected := test_config.get('expected_status')) and response.status_code != expected:
            result.update({
                'success': False,
                'status': 'failed',
                'error': f"Expected status {expected}, got {response.status_code}"
            })
        else:
            result.update({'success': True, 'status': 'passed'})
            
    except Exception as e:
        result.update({
            'end_time': time.time(),
            'duration': time.time() - start_time,
            'success': False,
            'status': 'error',
            'error': str(e),
            'metrics': {'response_time': (time.time() - start_time) * 1000}
        })
        
    return result

def generate_test_cases(api_key: str, feature_description: str, domain: str = None) -> dict:
    """Generate test cases using AI"""
    base_url = next((part.split("\n")[0].strip() 
                   for part in feature_description.lower().split("base url:")[1:2] 
                   if part.strip()), "https://petstore.swagger.io/v2")
    
    prompt = f"""Generate 5-7 API test cases for the following API:
    {feature_description}
    
    Base URL: {base_url}
    
    For each test case, include these fields:
    - name: Short descriptive name
    - description: Detailed description of what the test verifies
    - method: HTTP method (GET, POST, etc.)
    - url: Full URL including path parameters (e.g., /posts/1)
    - headers: Any required headers
    - body: Request body (for POST/PUT)
    - expected_status: Expected HTTP status code
    - params: Query parameters (if any)
    
    Return as a JSON object with a 'test_cases' array containing the test cases.
    Example format:
    {{
        "test_cases": [
            {{
                "name": "Get all posts",
                "description": "Verify that GET /posts returns a 200 status code",
                "method": "GET",
                "url": "https://jsonplaceholder.typicode.com/posts",
                "expected_status": 200
            }}
        ]
    }}"""
        
    response = OpenAI(api_key=api_key).chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Generate concise API test cases in JSON format"},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"},
        temperature=0.3
    )
    
    result = json.loads(response.choices[0].message.content)
    return result


def init_session_state():
    """Initialize all session state variables in one place"""
    defaults = {
        'test_blocks': [],
        'test_results': {},
        'feature_description': "",
        'expanded_tests': {},
        'test_submitted': False,
        'test_cases_md': "",
        'domain': 'General',
        'test_type': 'Unit'
    }
    st.session_state.update({k: v for k, v in defaults.items() if k not in st.session_state})

def render_sidebar(api_key: str) -> None:
    """Render the sidebar with settings and controls"""
    with st.sidebar:
        st.caption("✅ API Key found" if api_key else "⚠️ No API Key found")

def main():
    """Main function to run the Streamlit app"""
    st.set_page_config(layout="wide", page_title="API Test Agent")
    init_session_state()
    
    if not (api_key := os.getenv('OPENAI_API_KEY')):
        st.error("Please set OPENAI_API_KEY in your .env file")
        return
    
    render_sidebar(api_key)
    
    st.title("API Test Agent")
    
    # Top row with three columns
    col_feature, col_chart, col_summary = st.columns([6, 3, 1])
    
    with col_feature:
        # Feature description input
        feature_desc = st.text_area(
            "Describe the feature to test:",
            height=200,
            placeholder="Example: User login with email/password and Base URL: https://jsonplaceholder.typicode.com"
        )
        
        # Action buttons below the feature input
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            if st.button("🤖 Generate Tests", use_container_width=True, type="primary"):
                if not feature_desc.strip():
                    st.error("Please enter a feature description")
                else:
                    st.session_state.feature_description = feature_desc
                    st.session_state.test_submitted = True
                    st.rerun()
        
        with btn_col2:
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.feature_description = ""
                st.session_state.test_submitted = False
                st.rerun()
    
    with col_chart:
        # Placeholder for the chart that will be updated after tests are run
        if st.session_state.get('test_results'):
            methods = []
            statuses = []
            
            for result in st.session_state.test_results.values():
                method = result.get('request', {}).get('method', 'GET').upper()
                status = 'PASS' if result.get('success') else 'FAIL'
                methods.append(method)
                statuses.append(status)
            
            if methods:
                df = pd.DataFrame({'method': methods, 'status': statuses})
                cross_tab = pd.crosstab(df['method'], df['status'], dropna=False)
                
                for col in ['PASS', 'FAIL']:
                    if col not in cross_tab.columns:
                        cross_tab[col] = 0
                
                cross_tab = cross_tab[['PASS', 'FAIL']]
                
                fig, ax = plt.subplots(figsize=(4, 3))
                cross_tab.plot(kind='bar', stacked=True, ax=ax, 
                             color=['#4CAF50', '#F44336'])
                
                plt.title('Test Results', fontsize=10)
                plt.xlabel('')
                plt.xticks(rotation=0, fontsize=8)
                plt.yticks(fontsize=8)
                plt.legend(title='', fontsize=8)
                plt.tight_layout()
                
                st.pyplot(fig, use_container_width=True)
    
    with col_summary:
        # Summary metrics
        if st.session_state.get('test_results'):
            methods = [result.get('request', {}).get('method', 'GET').upper() 
                      for result in st.session_state.test_results.values()]
            statuses = ['PASS' if result.get('success') else 'FAIL' 
                       for result in st.session_state.test_results.values()]
            
            if methods:
                df = pd.DataFrame({'method': methods, 'status': statuses})
                total = len(df)
                passed = len(df[df['status'] == 'PASS'])
                failed = total - passed
                
                st.markdown("""
                <div style='margin-bottom: 10px;'>
                    <div style='font-size: 12px; color: #6c757d;'>Total Tests</div>
                    <div style='font-size: 20px; font-weight: bold;'>{}</div>
                </div>
                <div style='margin-bottom: 10px;'>
                    <div style='font-size: 12px; color: #6c757d;'>Passed</div>
                    <div style='font-size: 20px; font-weight: bold; color: #28a745;'>{}</div>
                </div>
                <div>
                    <div style='font-size: 12px; color: #6c757d;'>Failed</div>
                    <div style='font-size: 20px; font-weight: bold; color: #dc3545;'>{}</div>
                </div>
                """.format(total, passed, failed), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style='margin-bottom: 10px;'>
                <div style='font-size: 12px; color: #6c757d;'>Total Tests</div>
                <div style='font-size: 20px; font-weight: bold;'>-</div>
            </div>
            <div style='margin-bottom: 10px;'>
                <div style='font-size: 12px; color: #6c757d;'>Passed</div>
                <div style='font-size: 20px; font-weight: bold; color: #28a745;'>-</div>
            </div>
            <div>
                <div style='font-size: 12px; color: #6c757d;'>Failed</div>
                <div style='font-size: 20px; font-weight: bold; color: #dc3545;'>-</div>
            </div>
            """, unsafe_allow_html=True)
    
    if st.session_state.test_submitted and not st.session_state.get('test_blocks'):
        with st.spinner("Generating test cases..."):
            try:
                response = generate_test_cases(
                    api_key,
                    st.session_state.feature_description,
                    st.session_state.domain
                )
                
                test_blocks = []
                for i, tc in enumerate(response.get('test_cases', [])):
                    if not isinstance(tc, dict):
                        continue
                        
                    # Set defaults and generate test name
                    tc.setdefault('method', 'GET')
                    tc.setdefault('expected_status', 200)
                    
                    # Handle both 'url' and 'endpoint' fields
                    if 'endpoint' in tc and 'url' not in tc:
                        tc['url'] = tc.pop('endpoint')
                    
                    if 'url' not in tc:
                        continue
                        
                    method = tc['method'].upper()
                    url_parts = tc['url'].split('?')
                    endpoint = url_parts[0].split('/')[-1] or 'endpoint'
                    param_str = ', '.join(f"{k}={v}" for k, v in tc.get('params', {}).items())
                    
                    test_blocks.append({
                        'code': json.dumps(tc, indent=2),
                        'name': f"{method} {endpoint} - {f'with {param_str} ' if param_str else ''}(Expected: {tc['expected_status']})",
                        'description': f"Test case for {method} {endpoint} with status {tc['expected_status']}"
                    })
                
                if test_blocks:
                    st.session_state.test_blocks = test_blocks
                    st.session_state.test_results = {}
                    st.session_state.expanded_tests = {i: False for i in range(len(test_blocks))}
                else:
                    st.warning("No valid test cases were generated")
                
            except Exception as e:
                st.error(f"Error generating test cases: {str(e)}")
            finally:
                st.session_state.test_submitted = False
        
    # Display test cases if we have them
    if st.session_state.get('test_blocks'):
        # Reset test_submitted flag to prevent regeneration
        st.session_state.test_submitted = False
        
        # Add a divider before the test cases
        st.write("---")
        
            # Test execution controls
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("Run All Tests"):
                run_all_tests()
        with col2:
            if st.button("Rerun Failed"):
                run_failed_tests()
        with col3:
            st.download_button(
                label="Download Tests",
                data=st.session_state.get('test_cases_md', ''),
                file_name="api_test_cases.md",
                mime="text/markdown"
            )
        
        st.write("")
        
        # Show test results header
        st.write(f"**Test Results ({len(st.session_state.test_blocks)} tests)**")
        
        for i, block in enumerate(st.session_state.test_blocks):
            test_name = block.get('name', f"Test {i+1}")
            
            # Create two columns for each test
            col1, col2 = st.columns([1, 2])
            
            with col1:
                # Left column: Test status and URL
                if i in st.session_state.test_results:
                    result = st.session_state.test_results[i]
                    request = result.get('request', {})
                    method = request.get('method', 'GET').upper()
                    url = request.get('url', 'No URL')
                    
                    # Style for different HTTP methods
                    if method == 'POST':
                        style = "color: #FF6B6B; font-weight: bold;"
                    else:
                        style = ""
                    
                    if result.get('success'):
                        st.markdown(f"✅ <span style='{style}'>{method}</span> - {url}", unsafe_allow_html=True)
                    else:
                        st.markdown(f"❌ <span style='{style}'>{method}</span> - {url}", unsafe_allow_html=True)
                else:
                    st.write(f"⏳ {test_name}")
            
            with col2:
                # Right column: Request/response details
                if i in st.session_state.test_results:
                    result = st.session_state.test_results[i]
                    request = result.get('request', {})
                    response = result.get('response', {})
                    
                    # Show request details
                    with st.expander("Request/Response Details"):
                        st.write("**Request:**")
                        st.code(f"{request.get('method', 'GET')} {request.get('url', '')}\n"
                              f"Headers: {json.dumps(request.get('headers', {}), indent=2)}\n"
                              f"Body: {json.dumps(request.get('body', {}), indent=2) if request.get('body') else 'None'}",
                              language='http')
                        
                        # Show response details with scrollable area
                        st.write("**Response:**")
                        status_code = response.get('status_code', 'N/A')
                        status_emoji = '✅' if str(status_code).startswith('2') else '❌'
                        
                        # Create a scrollable text area for the response
                        response_text = f"Status: {status_emoji} {status_code}\n" \
                                     f"Headers: {json.dumps(response.get('headers', {}), indent=2)}\n" \
                                     f"Body: {json.dumps(response.get('body', {}), indent=2) if response.get('body') else 'None'}"
                        
                        st.text_area(
                            "Response Details",
                            value=response_text,
                            height=200,
                            key=f"response_{i}",
                            disabled=True,
                            label_visibility="collapsed"
                        )
                        
                        # Show error if any
                        if 'error' in result:
                            st.write("**Error:**")
                            st.error(result['error'])
            

def run_all_tests() -> bool:
    """Run all test blocks and update results"""
    if not (blocks := st.session_state.get('test_blocks')):
        st.warning("No test cases available to run")
        return False
    
    st.session_state.test_results = {
        i: run_single_test(i, block) 
        for i, block in enumerate(blocks)
        if run_single_test(i, block)
    }
    st.session_state.test_executed = True
    st.rerun()
    return True

def run_failed_tests() -> bool:
    """Run only the tests that previously failed"""
    if not (results := st.session_state.get('test_results')):
        st.warning("No test results available. Run tests first.")
        return False
    
    failed_tests = [i for i, r in results.items() if not r.get('success', True)]
    if not failed_tests:
        st.success("No failed tests to rerun!")
        return False
    
    for i in failed_tests:
        if i < len(st.session_state.test_blocks):
            results[i] = run_single_test(i, st.session_state.test_blocks[i])
    
    st.session_state.test_executed = True
    st.rerun()
    return True

def run_single_test(index: int, block: Dict) -> Optional[Dict]:
    """Run a single test block and return the result using direct API calls"""
    test_result = {
        'name': block.get('name', f'Test {index + 1}'),
        'success': False,
        'status': 'running',
        'start_time': time.time(),
        'endpoint': block.get('url', ''),
        'method': block.get('method', 'GET')
    }
    
    try:
        with st.spinner(f"Running test {index + 1}..."):
            # Parse and validate test config
            try:
                test_config = json.loads(block['code'])
                if not isinstance(test_config, dict):
                    raise ValueError("Test configuration must be a JSON object")
            except json.JSONDecodeError as e:
                raise ValueError(f"Invalid test configuration: {str(e)}")
            
            # Execute test and update result
            result = execute_api_test(test_config)
            test_result.update({
                'success': result.get('success', False),
                'status': result.get('status', 'completed'),
                'output': json.dumps(result.get('response', {}), indent=2),
                'error': result.get('error'),
                'end_time': result.get('end_time'),
                'duration': result.get('duration'),
                'metrics': result.get('metrics', {}),
                'api_calls': [result]
            })
            
            # Add request/response details
            if req := result.get('request'):
                test_result.update({
                    'endpoint': req.get('url', ''),
                    'method': req.get('method', 'GET'),
                    'request': req
                })
            
            if resp := result.get('response'):
                test_result.update({
                    'status_code': resp.get('status_code'),
                    'response': resp
                })
            
            # Store results
            st.session_state.setdefault('test_results', {})[index] = test_result
            return test_result
            
    except Exception as e:
        test_result.update({
            'success': False,
            'status': 'error',
            'error': f"Error running test {index + 1}: {str(e)}",
            'end_time': time.time(),
            'duration': time.time() - test_result['start_time']
        })
        st.session_state.setdefault('test_results', {})[index] = test_result
        return test_result
        

if __name__ == "__main__":
    main()

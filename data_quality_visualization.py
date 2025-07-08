import streamlit as st
import pandas as pd
import numpy as np
from pandas.api.types import is_numeric_dtype
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats
import io

# Page configuration
st.set_page_config(
    page_title="Data Quality Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main {
        max-width: 1400px;
    }
    .metric-card {
        background-color: #2E3440;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stButton>button {
        width: 100%;
    }
    .stAlert {
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

def load_data(uploaded_file):
    """Load data from uploaded file"""
    try:
        if uploaded_file.name.endswith('.csv'):
            return pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            return pd.read_excel(uploaded_file)
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None
    except Exception as e:
        st.error(f"Error loading file: {str(e)}")
        return None



def main():
    st.title("📊 Data Quality & Bias Analyzer")
    st.write("Upload your dataset to analyze it for potential biases and data quality issues.")
    
    # File upload
    uploaded_file = st.file_uploader("Choose a CSV or Excel file", type=['csv', 'xlsx', 'xls'])
    
    if uploaded_file is not None:
        # Load data
        df = load_data(uploaded_file)
        
        if df is not None:
            st.sidebar.header("Analysis Settings")
            
            # Display basic info
            st.sidebar.write(f"**File:** {uploaded_file.name}")
            st.sidebar.write(f"**Shape:** {df.shape[0]} rows, {df.shape[1]} columns")
            
            # Show data preview
            st.subheader("Data Preview")
            st.dataframe(df.head())
            
            # --- Data Profiling ---
            st.subheader("Data Profiling")
            numeric_cols = df.select_dtypes(include=np.number).columns.tolist()
            if numeric_cols:
                sel_cols = st.multiselect("Select numeric columns to profile:", options=numeric_cols, default=numeric_cols[:min(3, len(numeric_cols))])
                if sel_cols:
                    prof_tab1, prof_tab2 = st.tabs(["Histograms", "Boxplots"])

                    with prof_tab1:
                        cols_per_row = 3
                        for i, col in enumerate(sel_cols):
                            if i % cols_per_row == 0:
                                row_cols = st.columns(cols_per_row)
                            fig_hist = px.histogram(df, x=col, nbins=30, title=f"Histogram of {col}")
                            row_cols[i % cols_per_row].plotly_chart(fig_hist, use_container_width=True)

                    with prof_tab2:
                        cols_per_row = 3
                        for i, col in enumerate(sel_cols):
                            if i % cols_per_row == 0:
                                row_cols = st.columns(cols_per_row)
                            fig_box = px.box(df, y=col, title=f"Boxplot of {col}")
                            row_cols[i % cols_per_row].plotly_chart(fig_box, use_container_width=True)
                else:
                    st.info("Please select at least one numeric column to profile.")
            else:
                st.info("No numeric columns available for profiling.")
            
            # Data quality report
            st.subheader("Data Quality Report")
            
            # Basic statistics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Rows", len(df))
            with col2:
                st.metric("Missing Values", df.isnull().sum().sum())
            with col3:
                st.metric("Duplicate Rows", df.duplicated().sum())

            # --- Statistical Analysis ---
            st.subheader("Statistical Analysis")
            tab1, tab2, tab3, tab4 = st.tabs(["Descriptive Stats", "Missing Values", "Outliers", "Correlation"])

            with tab1:
                st.write("Descriptive statistics for numeric columns:")
                st.dataframe(df.describe().T)

            with tab2:
                st.write("Missing values per column:")
                st.dataframe(df.isnull().sum().to_frame(name='missing_count'))

            with tab3:
                st.write("Potential outliers detected via IQR method:")
                outlier_counts = {}
                for col in df.select_dtypes(include=np.number).columns:
                    Q1 = df[col].quantile(0.25)
                    Q3 = df[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower = Q1 - 1.5 * IQR
                    upper = Q3 + 1.5 * IQR
                    outlier_counts[col] = int(((df[col] < lower) | (df[col] > upper)).sum())
                st.dataframe(pd.Series(outlier_counts, name='outlier_count'))

            with tab4:
                numeric_cols = df.select_dtypes(include=np.number)
                if numeric_cols.shape[1] >= 2:
                    corr = numeric_cols.corr()
                    fig_corr = px.imshow(corr, text_auto=".2f", aspect="auto", color_continuous_scale='RdBu')
                    st.plotly_chart(fig_corr, use_container_width=True)
                else:
                    st.info("Not enough numeric columns for correlation heatmap.")
    
    # Add some space at the bottom
    st.markdown("---")
    st.markdown("""
    """)

if __name__ == "__main__":
    # Import plotly submodules after streamlit to avoid conflicts
    from plotly.subplots import make_subplots
    main()

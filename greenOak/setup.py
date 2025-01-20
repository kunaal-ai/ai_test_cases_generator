from setuptools import setup, find_packages

setup(
    name="greenoak",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "torch>=2.0.0",
        "transformers>=4.30.0",
        "datasets>=2.12.0",
        "scikit-learn>=1.2.2",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "matplotlib>=3.7.1",
        "seaborn>=0.12.2",
        "tensorboard>=2.13.0",
        "tqdm>=4.65.0",
        "python-dotenv>=1.0.0",
        "streamlit>=1.24.0",
        "wandb>=0.15.0",
        "jsonschema>=4.17.3",
        "nltk>=3.8.1",
        "plotly>=5.13.0",
        "sentencepiece>=0.1.99"
    ],
)

from setuptools import setup, find_packages

setup(
    name="agentic-microsaas-shared",
    version="1.0.0",
    description="Shared models and database utilities for Agentic MicroSaaS",
    packages=find_packages(where="libs"),
    package_dir={"": "libs"},
    python_requires=">=3.8",
    install_requires=[
        "sqlalchemy>=2.0.0",
        "psycopg2-binary>=2.9.0",
        "python-dotenv>=1.0.0",
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)

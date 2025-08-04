#!/usr/bin/env python3
"""
Setup script for the bigbrotr library
"""

from setuptools import setup, find_packages
import os

# Read the contents of README file
this_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# Read requirements from requirements.txt
with open(os.path.join(this_directory, 'requirements.txt'), encoding='utf-8') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="bigbrotr",
    version="0.1.0",
    author="BigBrotr Team",
    author_email="hello@bigbrotr.com",
    description="A comprehensive Python library for NOSTR protocol and relay management with PostgreSQL backend",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bigbrotr/bigbrotr",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Database",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Communications",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
            "pre-commit>=3.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.2.0",
            "sphinx-autodoc-typehints>=1.19.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "bigbrotr=bigbrotr.cli:main",
        ],
    },
    keywords="nostr, relay, postgresql, websocket, cryptocurrency, decentralized",
    project_urls={
        "Bug Reports": "https://github.com/Bigbrotr/bigbrotr/issues",
        "Source": "https://github.com/Bigbrotr/bigbrotr",
        "Documentation": "https://bigbrotr.readthedocs.io/",
    },
    include_package_data=True,
    zip_safe=False,
)
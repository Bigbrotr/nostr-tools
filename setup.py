"""
Setup configuration for nostr-tools package.

This module defines the package metadata and dependencies for the 
nostr-tools Python library.
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip()
                    and not line.startswith("#")]

setup(
    name="nostr-tools",
    version="0.1.0",
    author="Bigbrotr",
    author_email="hello@bigbrotr.com",
    description="A Python library for Nostr protocol interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Bigbrotr/nostr-tools",
    packages=find_packages(),
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
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "black>=21.0",
            "flake8>=3.9",
            "mypy>=0.812",
        ],
    },
)

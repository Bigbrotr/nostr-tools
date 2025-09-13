#!/usr/bin/env python
"""Setup file for backward compatibility and complete metadata."""

from setuptools import find_packages, setup

# Read the README for the long description
with open("README.md", encoding="utf-8") as fh:
    long_description = fh.read()

VERSION = "0.1.0"

setup(
    name="nostr-tools",
    version=VERSION,
    author="Bigbrotr",
    author_email="hello@bigbrotr.com",
    description="A comprehensive Python library for Nostr protocol interactions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/bigbrotr/nostr-tools",
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Communications",
        "Topic :: Security :: Cryptography",
        "Framework :: AsyncIO",
    ],
    python_requires=">=3.9",
    install_requires=[
        "secp256k1>=0.14.0,<1.0.0",
        "bech32>=1.2.0,<2.0.0",
        "aiohttp>=3.8.0,<4.0.0",
        "aiohttp-socks>=0.8.0,<1.0.0",
        "typing-extensions>=4.0.0; python_version<'3.10'",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0,<9.0.0",
            "pytest-asyncio>=0.24.0,<1.0.0",
            "pytest-cov>=5.0.0,<6.0.0",
            "pytest-mock>=3.14.0,<4.0.0",
            "ruff==0.8.6",
            "mypy>=1.14.0,<2.0.0",
            "pre-commit>=4.0.0,<5.0.0",
            "build>=1.0.0",
            "twine>=6.0.0",
        ],
        "test": [
            "pytest>=8.0.0,<9.0.0",
            "pytest-asyncio>=0.24.0,<1.0.0",
            "pytest-cov>=5.0.0,<6.0.0",
            "pytest-mock>=3.14.0,<4.0.0",
        ],
        "security": [
            "bandit[toml]>=1.8.0,<2.0.0",
            "safety>=3.0.0,<4.0.0",
            "pip-audit>=2.7.0,<3.0.0",
        ],
        "docs": [
            "sphinx>=8.0.0,<9.0.0",
            "sphinx-rtd-theme>=3.0.0,<4.0.0",
            "myst-parser>=4.0.0,<5.0.0",
        ],
        "perf": [
            "pytest-benchmark>=5.0.0,<6.0.0",
            "memory-profiler>=0.61.0,<1.0.0",
            "py-spy>=0.4.0,<1.0.0",
        ],
    },
    package_data={
        "nostr_tools": ["py.typed"],
    },
    include_package_data=True,
    license="MIT",
    keywords=[
        "nostr",
        "decentralized",
        "social",
        "protocol",
        "websocket",
        "cryptography",
        "bitcoin",
        "schnorr",
        "secp256k1",
        "relay",
    ],
    project_urls={
        "Homepage": "https://github.com/bigbrotr/nostr-tools",
        "Documentation": "https://github.com/bigbrotr/nostr-tools#readme",
        "Repository": "https://github.com/bigbrotr/nostr-tools.git",
        "Bug Reports": "https://github.com/bigbrotr/nostr-tools/issues",
        "Source Code": "https://github.com/bigbrotr/nostr-tools",
        "Changelog": "https://github.com/bigbrotr/nostr-tools/blob/main/CHANGELOG.md",
    },
    zip_safe=False,
)

#!/usr/bin/env python
"""Setup file for backward compatibility and metadata inclusion."""

from setuptools import find_packages, setup

VERSION = "0.1.0"

setup(
    name="nostr-tools",
    version=VERSION,
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    python_requires=">=3.9",
)

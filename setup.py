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
    url="https://github.com/bigbrotr/nostr-tools",  # Update with your repo URL
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
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Communications",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    keywords="nostr, decentralized, social, protocol, websocket",
    project_urls={
        "Bug Reports": "https://github.com/bigbrotr/nostr-tools/issues",
        "Source": "https://github.com/bigbrotr/nostr-tools",
    },
)

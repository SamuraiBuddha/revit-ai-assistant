"""Setup configuration for Revit AI Assistant"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="revit-ai-assistant",
    version="0.1.0",
    author="Jordan Ehrig",
    description="Multi-agent AI system for Autodesk Revit using local LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SamuraiBuddha/revit-ai-assistant",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.9",
    install_requires=[
        "pydantic>=2.0",
        "pydantic-ai>=0.1.0",
        "httpx>=0.24.0",
        "aiofiles>=0.8.0",
        "python-dotenv>=1.0.0",
        "PyYAML>=6.0",
        "chromadb>=0.4.0",
        "sentence-transformers>=2.2.0",
        "pythonnet>=3.0.0",
        "websockets>=11.0",
        "aioredis>=2.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ],
        "llm": [
            "llama-cpp-python>=0.2.0",
            "transformers>=4.30.0",
        ],
        "docs": [
            "mkdocs>=1.4.0",
            "mkdocs-material>=9.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "revit-ai-server=server.mcp_server:main",
            "revit-ai-setup=scripts.setup_models:main",
        ],
    },
    package_data={
        "revit_ai_assistant": [
            "config/*.yaml",
            "knowledge/data/standards/**/*",
        ],
    },
    include_package_data=True,
)
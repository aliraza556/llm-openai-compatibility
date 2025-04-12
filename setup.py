from setuptools import setup, find_packages

setup(
    name="llm-openai-compatibility",
    version="0.1.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A compatibility layer for using OpenAI Agents SDK with different LLM providers",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/llm-openai-compatibility",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.8",
    install_requires=[
        "openai-agents>=0.1.0",
        "openai>=1.0.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
) 
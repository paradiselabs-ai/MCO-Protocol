from setuptools import setup, find_packages

setup(
    name="mco-server",
    version="0.1.0",
    description="Model Configuration Orchestration Server - A framework-agnostic orchestration layer for reliable AI agent workflows",
    author="ParadiseLabs, LLC",
    author_email="developers@paradiselabs.co",
    url="https://github.com/paradiselabs-ai/MCO-Protocol",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.21.0",
        "pydantic>=1.10.7",
        "redis>=4.5.4",
    ],
    extras_require={
        "dev": [
            "pytest>=7.3.1",
            "black>=23.3.0",
            "isort>=5.12.0",
            "mypy>=1.2.0",
            "flake8>=6.0.0",
        ],
    },
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
    python_requires=">=3.8",
    entry_points={
        "console_scripts": [
            "mco=mco_server.cli:main",
        ],
    },
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
)

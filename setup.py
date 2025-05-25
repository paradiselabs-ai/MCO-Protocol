from setuptools import setup, find_packages

setup(
    name="mco-server",
    version="0.1.0",
    description="Model Configuration Orchestration (MCO) Server",
    author="ParadiseLabs, LLC",
    author_email="developers@paradiselabs.co",
    url="https://github.com/paradiselabs-ai/mco-server",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.21.1",
        "pydantic>=1.10.7",
        "pyyaml>=6.0",
        "requests>=2.28.2",
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
    python_requires=">=3.8",
)

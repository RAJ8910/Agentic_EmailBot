from setuptools import setup, find_packages
from typing import List

def get_requirements() -> List[str]:
    try:
        with open("requirements.txt", "r") as f:
            return [
                line.strip()
                for line in f.readlines()
                if line.strip() and not line.startswith("-e")
            ]
    except FileNotFoundError:
        print("requirements.txt file not found.")
        return []

setup(
    name="agentic-emailbot",
    version="0.1.0",
    packages=find_packages(),
    install_requires=get_requirements(),
)

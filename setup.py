"""
Script to install whatubinup2
"""
from pathlib import Path

from setuptools import setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

if __name__ == "__main__":
    setup(
        description="Python desktop client for managing time logging",
        author="TJTH",
        author_email="tim@tjth.co",
        url="https://github.com/teamjtharrison/whatubinup2",
        long_description=long_description,
        long_description_content_type="text/markdown",
        package_dir={"": "whatubinup2"},
        packages=[
            "bin",
        ],
    )

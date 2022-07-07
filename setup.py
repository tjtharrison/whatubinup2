"""
Script to install whatubinup2
"""
from glob import glob

from setuptools import find_packages, setup

if __name__ == "__main__":
    setup(
        data_files=[("whatubinup2", set(glob("*")) - set(glob("*.egg-info")))],
        description="Python desktop client for managing time logging",
        author="Tim Harrison",
        author_email="tim@tjth.co",
        url="https://github.com/teamjtharrison/what_u_bin_up_2",
        long_description = ("README.md").read_text(),
        long_description_content_type="text/markdown",
        packages=find_packages()
    )

"""
Script to install whatubinup2
"""
from glob import glob

import pypandoc
from setuptools import find_packages, setup

if __name__ == "__main__":
    setup(
        description="Python desktop client for managing time logging",
        author="Tim Harrison",
        author_email="tim@tjth.co",
        url="https://github.com/teamjtharrison/what_u_bin_up_2",
        long_description=pypandoc.convert_file("README.md", "rst"),
        long_description_content_type="text/markdown",
        package_dir = {'': 'whatubinup2'},
        packages= ['bin',]
    )

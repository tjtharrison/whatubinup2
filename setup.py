"""
Script to install whatubinup2
"""
from glob import glob

from setuptools import setup

if __name__ == "__main__":
    setup(data_files=[("whatubinup2", set(glob("*")) - set(glob("*.egg-info")))])

"""
Script to install whatubinup2
"""
from setuptools import setup
from glob import glob

if __name__ == "__main__":
    setup(
        data_files = [
        ('whatubinup2', glob('*', recursive=True))
        ]
    )

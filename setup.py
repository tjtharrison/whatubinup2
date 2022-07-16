"""
Placeholder required for wheel generation
Used by py2app to create .app
"""

from setuptools import setup

APP = ["src/whatubinup2/__main__.py"]
DATA_FILES = []
OPTIONS = {
    "iconfile": "img/wubu2.icns",
}

setup(
    app=APP,
    data_files=DATA_FILES,
    options={"py2app": OPTIONS},
    setup_requires=[],
)

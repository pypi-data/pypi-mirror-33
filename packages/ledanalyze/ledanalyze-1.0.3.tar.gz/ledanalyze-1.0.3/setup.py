"""
LED_Analyze - setup
Date: 15 June 2018
By: Ivan Pougatchev
Version: 1.0.3
"""
from setuptools import setup, find_packages

setup(
    name="ledanalyze",
    description="Process colorimetry data",
    version="1.0.3",
    url="https://github.com/pougivan/LED_Analyze",
    author="pougivan",
    packages=find_packages(),
    install_requires=[
        "numpy",
        "matplotlib",
        "openpyxl",
        ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License"
        ))

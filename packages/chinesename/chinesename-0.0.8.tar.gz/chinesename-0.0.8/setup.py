import setuptools
import register

import os

long_description = 'Add a fallback short description here'
if os.path.exists('README.rst'):
    long_description = open('README.rst').read()

setuptools.setup(
    name="chinesename",
    version="0.0.8",
    author="Peng Shiyu",
    author_email="pengshiyuyx@gmail.com",
    description="get a chinesename by random",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/mouday/chinesename",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    package_data = {
            # If any package contains *.txt or *.rst files, include them:
            'source': ['*.txt', "*.json"],
    }
)

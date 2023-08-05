#!/usr/bin/env python

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="FIXation",
    version="0.0.4",
    author="Alex Nordlund",
    author_email="deep.alexander@gmail.com",
    description="FIX repository tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/deepy/fixation",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    include_package_data=True,
    entry_points={
        'console_scripts': ['fix-parse=fixation.parse:main'],
    }
)

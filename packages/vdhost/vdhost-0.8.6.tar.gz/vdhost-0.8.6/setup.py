#!/usr/bin/env python
import os
from setuptools import find_packages, setup

project = "vdhost"
version = "0.8.6"

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    long_description = readme.read()

setup(
    name=project,
    version=version,
    description="Command line interface for Vectordash hosts.",
    long_description=long_description,
    author="Arbaz Khatib",
    author_email="contact@vectordash.com",
    url="https://github.com/Vectordash/vectordash-host",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    include_package_data=True,
    zip_safe=False,
    keywords="vectordash",
    install_requires=[
        "click>=6.7,<7",
        "requests>=2.18.4",
        "colored==1.3.5",
    ],
    setup_requires=[],
    dependency_links=[],
    entry_points={
        "console_scripts": [
            "vdhost = vdhost.main:cli",
        ],
    },
)

#!/usr/bin/env python
from setuptools import find_packages, setup

with open("requirements.txt", "r") as fs:
    reqs = [r for r in fs.read().splitlines() if (len(r) > 0 and not r.startswith("#"))]

with open("README.md", "r") as fs:
    long_description = fs.read()

__author__ = "walter.de.smedt@bics.com"
__license__ = "Apache License, version 2"

__version__ = "0.0.1"

setup(
    name="nornir_bics",
    version=__version__,
    description="Fork of Nornir with customized plugins",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author=__author__,
    url="https://github.com/nornir-automation/nornir",
    include_package_data=True,
    install_requires=reqs,
    packages=find_packages(exclude=("test*",)),
    license=__license__,
    test_suite="tests",
    platforms="any",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3.6",
    ],
)

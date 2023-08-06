#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

from prs import __version__

if sys.version_info < (3, 0):
    sys.exit("Sorry, Python 2 is not supported.")

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="prs",
    version=__version__,
    description="prs is a utility that allows you to use Python list comprehensions in shell commands.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Stavros Korokithakis",
    author_email="hi@stavros.io",
    url="https://gitlab.com/stavros/prs",
    packages=["prs"],
    package_dir={"prs": "prs"},
    install_requires=[],
    python_requires=">3.0.0",
    license="MIT",
    keywords="prs shell stdin",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    test_suite="tests",
    tests_require=[],
    entry_points={"console_scripts": ["prs=prs.cli:main"]},
)

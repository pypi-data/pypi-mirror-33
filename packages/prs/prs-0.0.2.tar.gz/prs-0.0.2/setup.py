#!/usr/bin/env python
# -*- coding: utf-8 -*-


from prs import __version__

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
    include_package_data=True,
    install_requires=[],
    license="MIT",
    zip_safe=True,
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

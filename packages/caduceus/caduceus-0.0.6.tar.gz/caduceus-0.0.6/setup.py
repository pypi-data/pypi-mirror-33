#!/usr/bin/env python
# -*- coding: utf-8 -*-


import sys

from caduceus import __version__

if sys.version_info < (3, 0):
    sys.exit("Sorry, Python 2 is not supported.")

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="caduceus",
    version=__version__,
    description="Caduceus notifies you if your scheduled tasks/cron jobs did not run.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Stavros Korokithakis",
    author_email="hi@stavros.io",
    url="https://gitlab.com/stavros/caduceus",
    packages=["caduceus"],
    package_dir={"caduceus": "caduceus"},
    install_requires=["apscheduler", "flask", "peewee", "toml", "schema", "pytimeparse"],
    python_requires=">3.0.0",
    license="MIT",
    keywords="caduceus tasks dead man switch notify",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    test_suite="tests",
    tests_require=[],
    entry_points={"console_scripts": ["caduceus=caduceus.cli:main"]},
)

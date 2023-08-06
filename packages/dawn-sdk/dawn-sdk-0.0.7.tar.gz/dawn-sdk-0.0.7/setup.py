#!/usr/bin/env python

import re

import setuptools

version = ""
with open('dawn_sdk/__init__.py', 'r') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dawn-sdk",
    version=version,
    author="TAL AI-LAB",
    author_email="author@example.com",
    description="This is the SDK for dawn, which is OSS system. Dawn is honorly presented by TAL's ocean team.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://dawn.shareurl.facethink.com",
    install_requires=[
        'requests!=2.9.0',
        'lxml>=4.2.3',
        'monotonic>=1.5',
    ],
    packages=setuptools.find_packages(exclude=("test")),
    classifiers=(
        "License :: OSI Approved :: MIT License",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5"
    ),
    exclude_package_data={'': ["dawn_sdk/test.py", "dawn_sdk/config.txt"]},
)


#!/usr/bin/env python
import setuptools

install_reqs = []

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='yaretry',
    version='0.1.1',
    description='Small library for a neat looking retry wrapper',
    long_description=long_description,
    author='Rami Amar',
    author_email='rami@alooma.com',
    url='https://github.com/Aloomaio/yaretry',
    packages=setuptools.find_packages(),
    install_requires=install_reqs,
    keywords=['alooma, retry'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    )
)


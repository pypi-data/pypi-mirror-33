#!/usr/bin/env python
import setuptools

install_reqs = []


setuptools.setup(
    name='yaretry',
    version='0.1.0',
    description='Small library for a neat looking retry wrapper',
    author='Rami Amar',
    author_email='rami@alooma.com',
    url='https://github.com/Aloomaio/yaretry',
    packages=setuptools.find_packages(),
    install_requires=install_reqs,
    keywords=['alooma, retry'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    )
)


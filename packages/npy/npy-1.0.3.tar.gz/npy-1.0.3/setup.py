#!/usr/bin/env python2
import setuptools
import os
with open("README.md", "r") as fh:
    long_description = fh.read()

install_requires     = ['argparse']

setuptools.setup(
    name                 = 'npy',
    python_requires      = '~=2.7',
    version              = '1.0.3',
    description          = "Normalize Python block and indentation technique.",
    long_description=long_description,
    scripts=[os.path.join("npy","normalyze.py")],
    packages=setuptools.find_packages(),
    author               = "ZviWex.",
    author_email         = "zvikizviki@gmail.com",
    url                  = 'https://ZviWex.com',
    install_requires     = install_requires,
    license              = "GNU",
    classifiers=(
        "Programming Language :: Python :: 2",
        "Operating System :: OS Independent",
    ),
)
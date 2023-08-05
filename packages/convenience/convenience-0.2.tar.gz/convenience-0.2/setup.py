# -*- coding: utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="convenience",
    version="0.2",
    author="Sylvain Raybaud",
    author_email="sylvain.raybaud@crans.org",
    description="Convenience tool: wrapper around regular/gzip files, Logger, text colors",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/sylvainraybaud/convenience",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ),
)

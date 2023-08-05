# -*- coding:utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="dt_utils",
    version="0.0.0",
    author="claydodo and his little friends (xiao huo ban)",
    author_email="claydodo@foxmail.com",
    description="Datetime utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/claydodo/dt_utils",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7 ",
        "Operating System :: OS Independent",
    ),
)

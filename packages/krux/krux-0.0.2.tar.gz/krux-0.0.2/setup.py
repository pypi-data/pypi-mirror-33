# -*- coding:utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="krux",
    version="0.0.2",
    author="claydodo and his little friends (xiao huo ban)",
    author_email="claydodo@foxmail.com",
    description="misc utils",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/claydodo/krux",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7 ",
        "Operating System :: OS Independent",
    ),
)

# -*- coding:utf-8 -*-

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="wrestful",
    version="0.0.0",
    author="claydodo and his little friends (xiao huo ban)",
    author_email="claydodo@foxmail.com",
    description="A variant of restful",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/claydodo/wrestful",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 2.7",
        "Framework :: Django",
        "Operating System :: OS Independent",
    ),
)

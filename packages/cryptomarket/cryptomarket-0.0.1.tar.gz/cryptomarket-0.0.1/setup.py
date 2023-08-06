# coding: utf-8

import os
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()
REQUIREMENTS = [line.strip() for line in open(os.path.join(os.path.dirname(__file__), 'requirements.txt')).readlines()]

setuptools.setup(
    name="cryptomarket",
    version="0.0.1",
    author="CryptoMarket",
    author_email="pablo@cryptomkt.com",
    description="CryptoMarket API client library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/cryptomkt/cryptomkt-python",
    include_package_data=True,
    packages=setuptools.find_packages(),
    install_requires=REQUIREMENTS,
    classifiers=(
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)    
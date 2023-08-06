#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name="ethereum_input_decoder",
    version="0.2.2",
    packages=["ethereum_input_decoder"],
    author="tintinweb",
    author_email="tintinweb@oststrom.com",
    description=(
        "Decode transaction inputs based on the contract ABI"),
    license="GPLv3",
    keywords=["ethereum", "blockchain", "input", "transaction", "decoder"],
    url="https://github.com/tintinweb/ethereum-input-decoder/",
    download_url="https://github.com/tintinweb/ethereum-input-decoder/tarball/v0.2.2",
    #python setup.py register -r https://testpypi.python.org/pypi
    long_description=read("README.rst") if os.path.isfile("README.rst") else read("README.md"),
    install_requires=["eth-abi", "requests"],
    package_data={
                  'ethereum_input_decoder': ['ethereum_input_decoder'],
                  },
)

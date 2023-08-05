#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
from setuptools import setup, find_packages
from os.path import expanduser

# Utility function to read the README file.
# Used for the long_description.  It's nice, because now 1) we have a top level
# README file and 2) it's easier to type in the README file than to put a raw
# string in below ...
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

# Default directories (they should match the ones in conf.py)
home_dir = expanduser("~") + "/" # Home dir (e.g: "/home/your_user_name/").
bitcoin_tools_dir = home_dir + 'bitcoin_tools/'  # Bitcoin_tools data dir.
address_vault = bitcoin_tools_dir + "bitcoin_addresses/"  # Address vault .
data_path = bitcoin_tools_dir + "data/"  # Data storage path (for IO).
figs_path = bitcoin_tools_dir + "figs/"  # Figure store dir, where images from analysis will be stored.

setup(
    name="python_bitcoin_tools",
    version="0.2.1",
    author="Sergi Delgado-Segura and Cristina Pérez-Solà",
    author_email = "sdelgado@deic.uab.cat, cperez@deic.uab.cat",
    description = ("Python library created for teaching and researching purposes."),
    license = "BSD 3",
    keywords = "bitcoin, transaction builder, key management, chainstate analysis",
    url = "https://github.com/sr-gi/bitcoin_tools",
    packages=find_packages(exclude=['examples', 'test']),
    data_files=[(bitcoin_tools_dir, []), (address_vault, []), (data_path, []), (figs_path, [])],
    include_package_data=True,
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Education",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Programming Language :: Python :: 2 :: Only"
    ],
    install_requires=['ecdsa', 'python-bitcoinlib', 'base58', 'qrcode', 'Pillow', 'plyvel', 'matplotlib', 'numpy', 'ujson'],
)



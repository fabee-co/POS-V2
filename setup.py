# -*- coding: utf-8 -*-
# Copyright (c) 2025, QFarmers and contributors
# For license information, please see license.txt

from setuptools import setup, find_packages

with open("requirements.txt") as f:
    install_requires = f.read().strip().split("\n")

# get version from __version__ variable in qfarmers_pos/__init__.py
from qfarmers_pos import __version__ as version

setup(
    name="qfarmers_pos",
    version=version,
    description="Custom POS application for QFarmers organic produce and grocery store in Chennai",
    author="QFarmers",
    author_email="info@qfarmers.com",
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    install_requires=install_requires
)

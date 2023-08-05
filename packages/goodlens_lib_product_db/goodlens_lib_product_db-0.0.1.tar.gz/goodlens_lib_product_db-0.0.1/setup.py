# coding: utf-8

"""
    goodlens_lib_product_db

    Utility package for goodlens-product-db

"""


import sys
from setuptools import setup, find_packages

NAME = "goodlens_lib_product_db"
VERSION = "0.0.1"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["pymongo"]

setup(
    name=NAME,
    version=VERSION,
    description="",
    author_email="swcbok@gmail.com",
    url="",
    keywords=["GoodLens", "goodlens_lib_product_db"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    """
)

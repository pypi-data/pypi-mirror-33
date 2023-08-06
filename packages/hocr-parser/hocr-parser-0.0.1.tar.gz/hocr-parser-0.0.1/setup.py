# coding: utf-8

"""
    hocr-parser

    This is a package for get json file from hocr file

    OpenAPI spec version: 0.0.1
    Contact: originman@bluehack.net
"""

from setuptools import setup, find_packages

NAME = "hocr-parser"
VERSION = "0.0.1"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["lxml"]

setup(
    name=NAME,
    version=VERSION,
    description="This is a package for get json file from hocr file",
    author_email="originman@bluehack.net",
    url="",
    keywords=["blu", "blu-trend"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
    """
)

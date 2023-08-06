#!/usr/bin/env python

from setuptools import setup, find_packages
import os
import codecs

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    README = f.read()

requires = ["requests", "pyyaml"]

setup(
      name='recordskeeper_python_lib3',
      version='0.1.1',
      description='RecordsKeeper Python library v3',
      long_description=README,
      long_description_content_type='text/markdown',
      classifiers=[
          "Programming Language :: Python"
      ],
      url='https://github.com/RecordsKeeper/recordskeeper-python-sdk/tree/python-3.0',
      keywords='recordskeeper, python3, library',
      packages=find_packages(),
      zip_safe=False,
      install_requires=requires,
      test_suite="test"
     )

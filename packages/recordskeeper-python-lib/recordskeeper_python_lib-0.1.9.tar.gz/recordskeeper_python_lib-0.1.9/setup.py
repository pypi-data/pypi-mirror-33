#!/usr/bin/env python

from setuptools import setup, find_packages
import os
import codecs

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    README = f.read()

requires = ["requests", "green", "pyyaml"]

setup(
      name='recordskeeper_python_lib',
      version='0.1.9',
      description='RecordsKeeper Python library',
      long_description=README,
      long_description_content_type='text/markdown',
      classifiers=[
          "Programming Language :: Python"
      ],
      url='https://github.com/RecordsKeeper/recordskeeper-python-sdk',
      keywords='recordskeeper, python, library',
      packages=find_packages(),
      zip_safe=False,
      install_requires=requires,
      test_suite="test"
     )

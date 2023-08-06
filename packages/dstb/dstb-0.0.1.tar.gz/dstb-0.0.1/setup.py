#!/usr/bin/python
# -*- coding: utf-8 -*-
import os

from setuptools import setup


def readme(file_name):
    if os.path.isfile(file_name):
        with open(file_name, 'r', encoding='UTF-8') as f:
            return f.read()


setup(name='dstb',
      version='0.0.1',
      description='A data science toolbox.',
      long_description=readme('README.md'),
      url='https://github.com/dnanhkhoa/dstb',
      author='Khoa Duong',
      author_email='dnanhkhoa@live.com',
      license='MIT',
      zip_safe=False)

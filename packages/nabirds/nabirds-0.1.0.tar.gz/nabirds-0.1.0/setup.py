#!/usr/bin/env python

import os
import pkg_resources
import sys

from setuptools import setup, find_packages
from pip.req import parse_requirements

install_requires = [line.strip() for line in open("requirements.txt").readlines()]

setup(
	name='nabirds',
	version='0.1.0',
	description='Wrapper for NA-Birds bataset (http://dl.allaboutbirds.org/nabirds)',
	author='Dimitri Korsch',
	author_email='korschdima@gmail.com',
	# url='https://chainer.org/',
	license='MIT License',
	packages=find_packages(),
	zip_safe=False,
	setup_requires=[],
	install_requires=install_requires,
    package_data={'': ['requirements.txt']},
    data_files=[('.',['requirements.txt'])],
    include_package_data=True,
	# tests_require=['mock', 'nose'],
)

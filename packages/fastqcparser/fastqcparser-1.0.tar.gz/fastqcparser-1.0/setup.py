#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import find_packages, setup

with open('README.md') as fh:
    long_description = fh.read()

setup(name='fastqcparser',
      version=open('VERSION').read().strip(),
      description='python API for parsing FastQC output',
      long_description=long_description,
      keywords = 'bioinformatics fastqc parsing',
      author='Adam Labadorf',
      author_email='labadorf@bu.edu',
      maintainer='Adam Labadorf',
      maintainer_email='labadorf@bu.edu',
      url='http://bitbucket.org/bubioinformaticshub/fastqcparser',
      packages=find_packages(),
      data_files=[],
      test_suite = 'discover_tests',
      classifiers=[
          'Development Status :: 5 - Production/Stable', 
          
          'Operating System :: MacOS :: MacOS X',
          'Operating System :: Microsoft :: Windows',
          'Operating System :: OS Independent',
          'Operating System :: POSIX',
          
          'Programming Language :: Python', 
          'Programming Language :: Python :: 2.7', 
          'Programming Language :: Python :: 3', 
          'Programming Language :: Python :: 3.3',
          'Programming Language :: Python :: 3.4',
          
          'Intended Audience :: Developers',
          'Intended Audience :: Science/Research',

          'Topic :: Scientific/Engineering :: Bio-Informatics',
          'Topic :: Software Development :: Libraries :: Python Modules',
          'Topic :: Utilities'
          ],
)

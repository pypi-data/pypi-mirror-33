#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 21:15:01 2018

@author: shubham
"""

from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='themodulex',
      version='0.2',
      description='Common utility functions for AI and Robotics research.',
      long_description=readme(),
      classifiers=[
             'License :: OSI Approved :: MIT License',
            'Programming Language :: Python :: 3.5',
      ],
      keywords='Artificial Intelligence Robotics Research Python AI ML Deep Learning',
      url='http://github.com/shubhamcxz',
      author='Shubham CXZ',
      author_email='shubhamcxz@gmail.com',
      license='MIT',
      packages=['themodulex'],
      username="shubhamcxz",
      install_requires=['numpy',],
      include_package_data=True,  # check what it does.
      test_suite='nose.collector',
      tests_require=['nose'],
      # dependency_links=['http://github.com/user/repo/tarball/master#egg=package-1.0'] # when dependency is not on pypi
      zip_safe=False,
      scripts=['bin/themodulex-cl-script'])

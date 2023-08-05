#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun 24 16:58:57 2018

@author: shashikant
"""

from setuptools import setup
 
#reading long description from file
with open('DESCRIPTION.txt') as file:
    long_description = file.read()
 
 
# specify requirements of your package here
REQUIREMENTS = ['numpy']
 
# some more details
CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Intended Audience :: Developers',
    'Topic :: Internet',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6', 
    ]
 
# calling the setup function 
setup(name='Fifteen-Puzzle-Game',
      version='0.0.1',
      description='A Simple Puzzle Game',
      long_description=long_description,
      url='https://github.com/skdhell/Fifteen-Puzzle-Game',
      author='ShashiKant Dwivedi',
      author_email='raghoram2009@gmail.com',
      license='MIT',
      packages=['Game'],
      classifiers=CLASSIFIERS,
      install_requires=REQUIREMENTS,
      keywords='Solving Puzzle'
      )

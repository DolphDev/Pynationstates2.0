#!/usr/bin/env python
"""
Copyright (c) 2016, 2017, 2018 Joshua Walters
"""


version = '0.0.1alpha'

from setuptools import setup
setup(name='nsapiwrapper',
      install_requires=["beautifulsoup4==4.6.0", "ezurl==0.1.3.25",
                        "requests==2.18.4", "xmltodict==0.11.0", "lxml==4.2.1" ],
      version=version,
      description='Simple Nationstates API Wrapper',
      author='Joshua W',
      author_email='DolphDevgithub@gmail.com',
      keywords=["nationstates"],
      packages=["nsapiwrapper"],
      classifiers=["License :: OSI Approved :: MIT License",
                   "Operating System :: OS Independent",
                   "Topic :: Utilities",
                   "Programming Language :: Python :: 3.2",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: 3.4",
                   "Programming Language :: Python :: 3.5",
                   "Programming Language :: Python :: 3.6"]
                    )

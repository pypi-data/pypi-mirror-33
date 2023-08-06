#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Setup file for kryptoflow.

    This file was generated with PyScaffold 3.0.3.
    PyScaffold helps you to put up the scaffold of your new Python project.
    Learn more under: http://pyscaffold.org/
"""

import sys
from setuptools import setup, find_packages

# Add here console scripts and other entry points in ini-style format


def setup_package():
    setup(version='0.2.2',
          install_requires=[
              'confluent-kafka==0.11.4',
              'avro-python3',
              'rx==1.6.1',
              'tweepy',
              'ws4py',
              'praw',
              'pandas',
              'nltk',
              'tweet-preprocessor==0.5.0',
              'tensorflow-gpu',
              'scikit-learn',
              'sortedcontainers',
              'kafka-tfrx'],
          keywords=[
              'kryptoflow',
              'tensorFlow',
              'deep-learning',
              'machine-learning',
              'data-science',
              'bitcoin',
              'kafka',
              'time-series'
          ],
          entry_points={"console_scripts": [
                  "kryptoflow = kryptoflow.main:cli",
              ],
          },
          classifiers=[
              'Programming Language :: Python',
              'Operating System :: OS Independent',
              'Intended Audience :: Developers',
              'Intended Audience :: Science/Research',
              'Topic :: Scientific/Engineering :: Artificial Intelligence'
          ],
          dependency_links=['git+git://github.com/Supervisor/supervisor.git@4.0.0.dev0#egg=supervisor4.0.0.dev0',
                            'git+git://github.com/danpaquin/gdax-python.git@1.0.6#egg=gdax-1.0.6'],

          tests_require=['pytest', 'pytest-cov', 'pytest-runner'],
          packages=find_packages())


if __name__ == "__main__":
    setup_package()

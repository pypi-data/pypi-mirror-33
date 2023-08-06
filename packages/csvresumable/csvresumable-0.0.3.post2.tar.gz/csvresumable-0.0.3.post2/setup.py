# -*- coding:utf-8 -*-

import os
import sys

from setuptools import setup, find_packages
here = os.path.abspath(os.path.dirname(__file__))
try:
    with open(os.path.join(here, 'README.md')) as f:
        README = f.read()
    with open(os.path.join(here, 'CHANGES.txt')) as f:
        CHANGES = f.read()
except IOError:
    README = CHANGES = ''

install_requires = []

docs_extras = ["kamidana"]

tests_require = []

testing_extras = tests_require + []

setup(
    name='csvresumable',
    version='0.0.3-2',
    description='adding tiny resume function, for csv reading iterator',
    long_description=README + '\n\n' + CHANGES,
    long_description_content_type='text/markdown',
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    keywords='csv, resume',
    author="podhmo",
    author_email="ababjam61+pypi@gmail.com",
    url="https://github.com/podhmo/csvresumable",
    packages=find_packages(exclude=["csvresumable.tests"]),
    include_package_data=True,
    zip_safe=False,
    install_requires=install_requires,
    extras_require={
        'testing': testing_extras,
        'docs': docs_extras,
    },
    tests_require=tests_require,
    test_suite="csvresumable.tests",
    entry_points="""
"""
)

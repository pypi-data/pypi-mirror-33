#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['Click>=6.0', 'pandas', 'pysam', 'pybedtools']

setup_requirements = ['pytest-runner']

test_requirements = ['pytest', 'beautifulsoup4', 'requests']

setup(
    author="Isabelle Berger",
    author_email='isabelle.c.berger@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Use pybedtools intersect to gain target gene information in pandas dataframes",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='targeneintersect',
    name='targeneintersect',
    packages=find_packages(include=['targeneintersect']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/isabelleberger/targeneintersect',
    version='0.2.2',
    zip_safe=False,
    dependency_links=['https://github.com/arq5x/bedtools2'],
)

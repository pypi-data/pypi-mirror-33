#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    README = readme_file.read()

with open('HISTORY.rst') as history_file:
    HISTORY = history_file.read()

try:
    with open('requirements_dev.txt') as requirements_file:
        DEV_REQUIREMENTS = requirements_file.read().splitlines()
except FileNotFoundError:  # tox builds
    DEV_REQUIREMENTS = []


REQUIREMENTS = []

SETUP_REQUIREMENTS = ['pytest-runner', ]

TEST_REQUIREMENTS = DEV_REQUIREMENTS

setup(
    author="Walter Danilo Galante",
    author_email='walterdangalante@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Minimal environment variables reader",
    install_requires=REQUIREMENTS,
    license="MIT license",
    long_description=README + '\n\n' + HISTORY,
    include_package_data=True,
    keywords='envi',
    name='envi',
    packages=find_packages(include=['envi']),
    package_data={'envi': ['requirements_dev.txt']},
    setup_requires=SETUP_REQUIREMENTS,
    test_suite='tests',
    tests_require=TEST_REQUIREMENTS,
    url='https://github.com/OvalMoney/envi',
    version='0.2.2',
    zip_safe=False,
)

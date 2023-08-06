#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup
import os

with open('README.md') as readme_file:
    readme = readme_file.read()

os.system("cp -rf ./build ./keeper-contracts")

requirements = []

setup_requirements = []

test_requirements = []

setup(
    author="leucothia",
    author_email='devops@oceanprotocol.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description=" 🐳 Integration of TCRs, CPM and Ocean Tokens in Solidity",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme,
    include_package_data=True,
    keywords='keeper-contracts',
    name='keeper-contracts',
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/oceanprotocol/keeper-contracts',
    version='0.0.1',
    zip_safe=False,
)

os.system("rm -rf ./keeper-contracts")

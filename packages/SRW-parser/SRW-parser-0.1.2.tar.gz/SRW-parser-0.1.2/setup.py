#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages
import versioneer

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('requirements.txt') as f:
    requirements = f.read().split()

setup_requirements = [ ]

test_requirements = [ ]

setup(
    name='SRW-parser',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    author="Kaleb Robert Swartz",
    author_email='kalebswartz7@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    description="Reads in a data file and vizualizes data withh image along with interactive horizontal and vertical cuts ",
    install_requires=requirements,
    license="Apache Software License 2.0",
    long_description=readme,
    include_package_data=True,
    keywords='SRW_parser',
    packages=find_packages(include=['SRW_parser']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/kalebswartz7/SRW-parser',
    zip_safe=False,
    entry_points={
        "console_scripts": ['SRW-parser=SRW_parser.SRW_parser:cli']
    },
)

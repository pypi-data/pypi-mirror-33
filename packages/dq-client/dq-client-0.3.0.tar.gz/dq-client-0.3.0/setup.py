#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'requests == 2.11.1'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='dq-client',
    version='0.3.0',
    description="Python library which allows to use http://dataquality.pl in easy way.",
    long_description=readme + '\n\n' + history,
    author="Mikołaj Olszewski",
    author_email='mikolaj.olszewski@algolytics.pl',
    url='https://github.com/Algolytics/dq_client',
    packages=[
        'dq',
    ],
    package_dir={'dq': 'dq'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords=['dataquality', 'dq', 'dq-client'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)

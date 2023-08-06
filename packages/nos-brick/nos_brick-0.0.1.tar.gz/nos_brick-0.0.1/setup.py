#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    # TODO: put package requirements here
    'os_brick',
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='nos_brick',
    version='0.0.1',
    description="Volume discovery and local storage management lib for non OpenStack deployments",
    long_description=readme + '\n\n' + history,
    author="Gorka Eguileor",
    author_email='geguileo@redhat.com',
    url='https://github.com/akrog/nos_brick',
    packages=[
        'nos_brick',
    ],
    package_dir={'nos_brick':
                 'nos_brick'},
    include_package_data=True,
    install_requires=requirements,
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='nos_brick',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)

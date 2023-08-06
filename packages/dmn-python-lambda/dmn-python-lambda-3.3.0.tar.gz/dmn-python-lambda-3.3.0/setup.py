#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

setup(
    name='dmn-python-lambda',
    version='3.3.0',
    description='The bare minimum for a Python app running on Amazon Lambda.',
    long_description=readme,
    author='Nick Ficano',
    author_email='nficano@gmail.com',
    url='https://github.com/nficano/python-lambda',
    packages=find_packages(),
    package_data={
        'aws_lambda': ['project_templates/*'],
        '': ['*.json'],
    },
    include_package_data=True,
    scripts=['scripts/lambda'],
    install_requires=[
        'boto3==1.4.4',
        'botocore==1.5.62',
        'click==6.6',
        'docutils==0.12',
        'jmespath==0.9.0',
        'pyaml==15.8.2',
        'python-dateutil==2.5.3',
        'PyYAML==3.11',
        'six==1.10.0',
        'futures; python_version < "3.0"',
    ],
    license='ISCL',
    zip_safe=False,
    keywords='python-lambda',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=[],
)

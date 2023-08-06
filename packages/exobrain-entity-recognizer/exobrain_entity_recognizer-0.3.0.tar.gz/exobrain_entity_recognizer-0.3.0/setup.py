#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'spacy>=2.0,<3.0',
    'ujson',
    'textblob'
]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Kyoung-Rok Jang",
    author_email='kyoungrok.jang@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="Entity recognizer for Exobrain project.",
    entry_points={
        'console_scripts': [
            'exobrain_entity_recognizer=exobrain_entity_recognizer.cli:main',
        ],
    },
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='exobrain_entity_recognizer',
    name='exobrain_entity_recognizer',
    packages=find_packages(include=['exobrain_entity_recognizer']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/kaist-irnlp/exobrain-entity-recognizer',
    version='0.3.0',
    zip_safe=False,
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.md') as readme_file:
    readme = readme_file.read()

requirements = ['Click>=6.0', 'requests']

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Acciaioli Valverde",
    author_email='acci.valverde@gmail.com',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
    description="Migacore Technologies Technical Coding Challenge Solution",
    entry_points={
        'console_scripts': [
            'build-org-chart=mcore_organization_chart.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    long_description_content_type='text/markdown',
    include_package_data=True,
    keywords='mcore_organization_chart',
    name='mcore_organization_chart',
    packages=find_packages(include=['mcore_organization_chart']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/spin14/mcore-organization-chart',
    version='1.0.0',
    zip_safe=False,
)

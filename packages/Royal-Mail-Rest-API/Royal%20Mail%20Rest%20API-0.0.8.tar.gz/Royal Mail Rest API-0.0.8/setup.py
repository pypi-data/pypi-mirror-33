#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = ['requests' ]

setup_requirements = ['pytest-runner', ]

test_requirements = ['pytest', ]

setup(
    author="Alex Hellier",
    author_email='alex.hellier@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="A small helper for integrating python with Royal Mails Rest API",
    entry_points={
        'console_scripts': [
            'royal_mail_rest_api=royal_mail_rest_api.cli:main',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='Royal Mail Rest API',
    name='Royal Mail Rest API',
    packages=find_packages(include=['royal_mail_rest_api']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    project_urls={'Source': 'https://github.com/bobspadger/royal_mail_rest_api',
                  'Documentation': 'http://royal-mail-rest-api.readthedocs.io/en/latest/index.html'},
    download_url='https://github.com/Bobspadger/royal_mail_rest_api',
    url='https://github.com/bobspadger/royal_mail_rest_api',
    version='0.0.8',
    zip_safe=False,
)

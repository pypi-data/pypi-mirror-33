#!/usr/bin/env python
# -*- coding: utf-8 -*-

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = [
    'apiwrapper'
]

test_requirements = [
    'pytest',
    'tox',
    'coverage',
    'pytest-cov',
]


setup(
    name='datalore',
    version='0.1.0',
    description="Data Interface Abstraction Library",
    long_description=readme + '\n\n' + history,
    author="Bobby Larson",
    author_email='bobby@robot.studio',
    url='https://github.com/RobotStudio/datalore',
    packages=find_packages(exclude=['docs', 'tests']),
    package_dir={'datalore':
                 'datalore'},
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='database database-connection-wrapper datalore db data-interface'
             'data-sync data-synchronization',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)

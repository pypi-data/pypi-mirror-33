#!/usr/bin/env python
# -*- coding: utf-8 -*-

def parse_requirements(filename):
    """ load requirements from a pip requirements file """
    lineiter = (line.strip() for line in open(filename))
    return [line for line in lineiter if line and not line.startswith("#")]

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read().replace('.. :changelog:', '')

requirements = parse_requirements(
    'requirements/prod.txt'
)

test_requirements = parse_requirements(
    'requirements/test.txt'
)


setup(
    name='astronaut',
    version='0.1.3',
    description="A framework for AI to explore spaces",
    long_description=readme + '\n\n' + history,
    author="Bobby Larson",
    author_email='bobby@robot.studio',
    url='https://github.com/RobotStudio/astronaut',
    packages=find_packages(exclude=['docs', 'tests']),
    package_dir={'astronaut':
                 'astronaut'},
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='astronaut',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements
)

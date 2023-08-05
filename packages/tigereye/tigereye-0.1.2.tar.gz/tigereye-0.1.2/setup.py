#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [ 'numpy', 'matplotlib' ]

setup_requirements = [ 'pytest-runner' ]

test_requirements = ['pytest' ]

setup(
    author="Youngsung Kim",
    author_email='grnydawn@gmail.com',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    description="A reusable data-mainupulation and plotting tool",
    entry_points={
        'console_scripts': [
            'tigereye=tigereye.tigereye:entry',
        ],
    },
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='tigereye',
    name='tigereye',
    packages=find_packages(include=['tigereye']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/grnydawn/tigereye',
    version='0.1.2',
    zip_safe=False,
)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages


def get_file_content(file_name):
    with open(file_name) as f:
        return f.read().strip()


setup(
    name='cloudshell-l1-networking-core',
    version=get_file_content('version.txt'),
    description='QualiSystems CloudShell L1 networking core package',
    author='QualiSystems',
    author_email='info@qualisystems.com',
    url='https://github.com/QualiSystems/cloudshell-l1-networking-core',
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    package_data={'core': ['data/*.yml', 'data/*.json', '*.txt']},
    entry_points={
        "console_scripts": ['build_driver = cloudshell.layer_one.tools.build_driver:build']
    },
    include_package_data=True,
    install_requires=get_file_content('requirements.txt'),
    license="Apache Software License 2.0",
    zip_safe=False,
    keywords='core cloudshell quali layer-one',
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Programming Language :: Python :: 2.7",
        "Topic :: Software Development :: Libraries",
        "License :: OSI Approved :: Apache Software License",
    ],
    test_suite='tests',
    tests_require=get_file_content('test_requirements.txt')
)

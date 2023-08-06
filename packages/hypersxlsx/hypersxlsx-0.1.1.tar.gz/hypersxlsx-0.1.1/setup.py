#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

import sys
import subprocess
from setuptools import setup, find_packages
from Cython.Build import cythonize
from distutils.core import setup
from distutils.extension import Extension

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

def lib():
    command = 'cd lib && make && make install'
    command_sudo = 'cd lib && make && make install'
    subprocess.call(command, shell=True)
    subprocess.call(command_sudo, shell=True)
    subprocess.call('python setup.py build_ext --inplace', shell=True)


if 'build_ext' not in sys.argv:
    lib()
ext_modules = cythonize(
    [Extension("cpexcel", ["src/cpexcel.pyx"], libraries=["xlsxwriter"])])

requirements = ['cython' ]

setup_requirements = [ ]

test_requirements = [ ]

setup(
    author="mum5",
    author_email='me@mum5.cn',
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
    description="hypers 用于写excel的库",
    install_requires=requirements,
    license="MIT license",
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='hypersxlsx',
    name='hypersxlsx',
    packages=find_packages(include=['src']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/mum5/hypersxlsx',
    version='0.1.1',
    zip_safe=False,
    ext_modules=cythonize(ext_modules)
)

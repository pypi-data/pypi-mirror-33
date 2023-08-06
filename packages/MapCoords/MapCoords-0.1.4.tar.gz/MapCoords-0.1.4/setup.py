# -*- coding: utf-8 -*-

from __future__ import print_function
from setuptools import setup, find_packages
import sys
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="MapCoords",
    version="0.1.4",
    description="A Python library about map coordinations",
    long_description=long_description,
    author='Ijustwantyouhappy',
    author_email='18817363043@163.com',
    maintainer='',
    maintainer_email='',
    license='MIT',
    packages=["MapCoords"],
    platforms=["all"],
    url='',
    install_requires=["numpy", "scipy", "pandas", "matplotlib", "h5py", "requests"],
    classifiers=[
        "Environment :: Web Environment",
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: MacOS',
        'Operating System :: Microsoft',
        'Operating System :: POSIX',
        'Operating System :: Unix',
        "Topic :: Internet",
        "Topic :: Software Development :: Libraries :: Python Modules",
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=True,
)
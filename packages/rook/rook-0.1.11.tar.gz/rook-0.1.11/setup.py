#!/usr/bin/env python

import os
import platform
import sys
import json
from glob import glob

try:
    # Use setuptools if available, for install_requires (among other things).
    import setuptools
    from setuptools import setup, Extension
except ImportError:
    setuptools = None
    from distutils.core import setup, Extension

# Classic setup.py

kwargs = {}

# Version configuration
with open('rook/rookout-config.json', 'r') as f:
    config = json.load(f)
version = config['VersionConfiguration']['VERSION']


# Readme
with open('README.rst') as f:
    kwargs['long_description'] = f.read()

if 'CPython' == platform.python_implementation():
    ext_modules = []

    if sys.platform in ('darwin', 'linux2', 'linux') and (
            (sys.version_info[0] == 2 and sys.version_info > (2, 7, 0)) or
            (sys.version_info[0] == 3 and sys.version_info > (3, 6, 0))):
        ext_modules.append(Extension(
            'rook.services.cdbg_native',
            sources=glob('rook/services/exts/cloud_debug_python/*.cc'),
            extra_compile_args=[
                '-std=c++0x',
                '-Werror',
                '-g0',
                '-O3']
            ))

    kwargs['ext_modules'] = ext_modules

if setuptools is not None:
    # If setuptools is not available, you're on your own for dependencies.
    install_requires = [
        "six==1.11",
        "grpcio >= 1.12.0, < 1.13.0",
        "protobuf==3.5.2"
    ]

    kwargs['install_requires'] = install_requires

setup(
    name="rook",
    version=version,
    packages=setuptools.find_packages(where='.', exclude=['contrib', 'docs', '*test*']),
    include_package_data=True,
    author="Rookout",
    author_email="liran@rookout.com",
    url="http://rookout.com/",
    description="Rook is a Python package for on the fly debugging and data extraction for application in production",
    license="https://github.com/Rookout/rookout.github.io/blob/master/agent/LICENSE.md",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',

        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',

        ],
    zip_safe=False,
    test_suite='tests',
    **kwargs
)

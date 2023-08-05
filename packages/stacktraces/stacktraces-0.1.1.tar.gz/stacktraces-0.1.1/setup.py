# -*- coding: utf-8 -*-
from __future__ import with_statement

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import os

from stacktraces import __version__


def read(fname):
    try:
        with open(os.path.join(os.path.dirname(__file__), fname), "r") as fp:
            return fp.read().strip()
    except IOError:
        return ''


setup(
    name="stacktraces",
    version=__version__,
    author="Germán Méndez Bravo",
    author_email="german.mb@gmail.com",
    url="https://github.com/Kronuz/stacktraces",
    license="MIT",
    description="Stack and stats tracer for multi-threaded applications.",
    long_description=read("README.rst"),
    py_modules=["stacktraces"],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
)

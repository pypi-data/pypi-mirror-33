#!/usr/bin/env python3

import sys
from os import path
from setuptools import setup


if sys.version_info < (3, 0):
    raise RuntimeError(
        "Sorry, but 'atomicloop' requires Python 3. But who uses 2.7 anyway?")


with open(path.join(path.dirname(__file__), 'README.rst')) as f:
    _LONG_DESCRIPTION = f.read().strip()


with open(path.join(path.dirname(__file__), 'atomicloop/__init__.py')) as f:
    for line in f:
        if line.startswith('__version__'):
            _VERSION = line.partition('=')[2].strip(' \n\'')
            break
    else:
        raise RuntimeError(
            "Couldn't find version in 'atomicloop/__init__.py'")


setup(
    name='atomicloop',
    long_description=_LONG_DESCRIPTION,
    version=_VERSION,
    description='Create atomic loop iterations (let the iteration finish even when interrupted)',
    author='Radek Kysely',
    author_email='kyselyradek@gmail.com',
    url='https://github.com/kysely/atomicloop',
    download_url='https://pypi.org/project/atomicloop/',
    license='MIT',

    packages=[
        'atomicloop'
    ],
    keywords=[
        'atomic',
        'linearizable',
        'undivisible',
        'uninterruptible',
        'atomic loop',
        'atomic block',
        'atomic operation',
        'delayed interrupt',
        'delayed keyboardinterrupt',
        'keyboardinterrupt',
        'SIGINT',
        'SIGTERM'
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)

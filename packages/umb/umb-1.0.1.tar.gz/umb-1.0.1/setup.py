# -*- coding: utf-8 -*-
"""
UMB Private API -- UMB information system's private API
=========================================

    >>> from umb import *

Links
`````

* `GitHub repository <https://github.com/fadhiilrachman/UMBPrivateAPI>`_

"""
from __future__ import with_statement
import re, codecs

try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

with open('umb/__about__.py') as f:
    version = re.search(r'__version__\s*=\s*\'(.+?)\'', f.read()).group(1)
assert version

with open('README.rst') as f:
    setup(
        name='umb',
        packages=['umb'],
        version=version,
        license='MIT License',
        author='Fadhiil Rachman',
        author_email='fadhiilrachman@gmail.com',
        url='https://github.com/fadhiilrachman/UMBPrivateAPI',
        description=' UMB information system\'s private API based on their mobile application',
        long_description=f.read(),
        classifiers=[
            'Development Status :: 4 - Beta',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.1',
            'Programming Language :: Python :: 3.2',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
            'Topic :: Communications :: Chat',
        ],
        install_requires=[
            'future',
            'requests'
        ],
    )
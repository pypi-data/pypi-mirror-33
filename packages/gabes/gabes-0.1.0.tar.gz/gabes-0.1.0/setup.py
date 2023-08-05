#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

readme = open('README.rst').read()
doclink = """
Documentation
-------------

The full documentation is at http://gabes.rtfd.org."""

setup(
    name='gabes',
    version='0.1.0',
    description='A pythonic library to use Garbled Circuits',
    long_description=readme + '\n\n' + doclink + '\n\n',
    author='Ignacio Navarro',
    author_email='nachonavarroasv@gmail.com',
    url='https://github.com/nachonavarro/gabes',
    packages=[
        'gabes',
    ],
    package_dir={'gabes': 'gabes'},
    include_package_data=True,
    install_requires=[
    ],
    license='MIT',
    zip_safe=False,
    entry_points = {
        'console_scripts': [
            'gabes = gabes.__main__:main'
        ]
    },
    keywords='gabes',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
)

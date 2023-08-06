#!/usr/bin/env python
# -*- coding: utf-8 -*-

from capture.version import __version__

from setuptools import setup, find_packages


url = 'https://github.com/SGBC/capture'

with open('README.md') as f:
    long_description = f.read()

setup(
    name='capture-assembler',
    version=__version__,

    description='The Capture seq assembler',
    long_description=long_description,
    long_description_content_type='text/markdown',

    url=url,
    download_url=url + '/tarball/' + __version__,
    author='Hadrien Gourlé, Renaud Van Damme',
    author_email='hadrien.gourle@slu.se',

    license='MIT',
    packages=find_packages(),

    tests_require=['nose', 'codecov'],
    install_requires=['doit', 'biopython', 'pysam'],
    include_package_data=True,

    entry_points={
        'console_scripts': ['capture = capture.app:main'],
    }
)

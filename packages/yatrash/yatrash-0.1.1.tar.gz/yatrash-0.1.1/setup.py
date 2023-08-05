#!/usr/bin/env python3

import pypandoc
from setuptools import setup, find_packages

long_description = pypandoc.convert('README.md', 'rst')

description = long_description.split('\n')[1]
print(description)
print(long_description)

classifiers='''
Natural Language :: English
Environment :: Console
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Operating System :: OS Independent
Programming Language :: Python :: 3.6
Topic :: Utilities
'''

setup(
    name='yatrash',
    version='0.1.1',
    description=description,
    author='Samuel Grayson',
    author_email='sam@samgrayson.me',
    url='https://github.com/charmoniumQ/yatrash/',
    packages=find_packages(),
    long_description=long_description,
    python_requires='>=3.6.0',
    entry_points = {
        "console_scripts": [
            'trash = yatrash.__main__:main',
        ],
    },
    classifiers=[classifier.strip()
                 for classifier in classifiers.strip().split('\n')],
)

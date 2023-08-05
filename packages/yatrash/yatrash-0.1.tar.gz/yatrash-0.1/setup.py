#!/usr/bin/env python3

from setuptools import setup, find_packages

with open('README.md') as f:
    long_description = f.read()

description = long_description.split('\n')[1]

classifiers='''
Natural Language :: English
Environment :: Console
License :: OSI Approved :: GNU General Public License v3 (GPLv3)
Operating System :: OS Independent
Programming Language :: Python :: 3.6
Topic :: Utilities
'''

print(find_packages())

setup(
    name='yatrash',
    version='0.1',
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

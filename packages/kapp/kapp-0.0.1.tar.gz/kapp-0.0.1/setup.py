#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='kapp',
    version='0.0.1',
    description='Deploy and manage SSL-supported web apps on Kubernetes clusters.',
    author='Steven Normore',
    author_email='steven@normore.me',
    url='https://github.com/snormore/kapp/',
    packages=find_packages(exclude=['tests', '.cache', '.venv', '.git', 'dist']),
    scripts=[
    ],
    install_requires=[
        'click',
        'shell',
    ],
    entry_points='''
        [console_scripts]
        kapp=kapp.cli:cli
    ''',
)

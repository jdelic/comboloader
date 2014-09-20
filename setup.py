#!/usr/bin/env python

try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

setup(
    name='mn-comboloader',
    version='0.1.2',
    description='A python/django based combo loader for javascript and css',
    long_description='comboloader (a fork of djamboloader (for django combo loader)) is a simple django application used to load and combine a list of javascript or css files from the filesystem for a specific library.',
    author='@jdelic',
    url='https://github.com/jdelic/comboloader',
    classifiers=[
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development"
    ],
    packages=[
        'comboloader',
    ],
    install_requires=[
        'Django>=1.6,<1.7',
        'django-cache-url',
        'gunicorn>=19,<20',
    ]
)


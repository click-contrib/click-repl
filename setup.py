#!/usr/bin/env python

from setuptools import setup

setup(
    name='click-repl',
    version='0.1',
    description='REPL plugin for Click',
    author='Markus Unterwaditzer',
    author_email='markus@unterwaditzer.net',
    url='https://github.com/untitaker/click-repl',
    license='MIT',
    packages=['click_repl'],
    install_requires=[
        'click',
        'prompt_toolkit',
        'six',
    ],
)

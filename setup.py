#!/usr/bin/env python

import ast
import re
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')


with open('click_repl/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='click-repl',
    version=version,
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

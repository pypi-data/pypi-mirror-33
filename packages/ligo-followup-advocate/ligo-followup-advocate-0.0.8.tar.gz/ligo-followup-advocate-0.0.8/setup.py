import ast
import sys

from setuptools import setup

# Get docstring and version without importing module
with open('ligo/followup_advocate/version.py') as f:
    mod = ast.parse(f.read())
__version__ = mod.body[-1].value.s

setup_requires = ['setuptools >= 30.3.0']
if {'pytest', 'test', 'ptr'}.intersection(sys.argv):
    setup_requires.append('pytest-runner')

setup(setup_requires=setup_requires, version=__version__)

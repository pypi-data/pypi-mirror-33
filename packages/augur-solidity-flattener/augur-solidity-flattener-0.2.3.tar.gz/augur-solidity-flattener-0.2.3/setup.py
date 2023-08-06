#!python3

from setuptools import setup, find_packages

setup(
    name='augur-solidity-flattener',
    description='Flattens Solidity code that uses imports into a single file. (Augur Fork)',
    author='Scott Bigelow, Forecast Foundation',
    author_email='team@augur.net',
    url='https://github.com/AugurProject/solidity-flattener',
    version='0.2.3',
    packages=find_packages(exclude=["*tests"]),
    scripts=['bin/solidity_flattener']
)

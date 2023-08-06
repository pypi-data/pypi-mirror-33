# -*- coding: utf-8 -*-

# Learn more: https://github.com/kennethreitz/setup.py

from setuptools import setup, find_packages

setup(
    name='broker_client',
    version='0.2.2',
    description='A client for the IoT Broker written in Python',
    author='Geovane Fedrecheski',
    packages=find_packages(exclude=('tests', 'docs'))
)

print(find_packages())

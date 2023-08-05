import inspect
import os

from setuptools import setup, find_packages

setup(
    name='domain-count-spider',
    version='0.0.3',
    description='Scrapy spider ',
    url='https://github.com/ricbartm/domain-count-spider',
    author='Ricardo Bartolome',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'scrapy>=1.5.0'
    ]
)

import inspect
import os

from setuptools import setup, find_packages

__location__ = os.path.join(
    os.getcwd(), os.path.dirname(inspect.getfile(inspect.currentframe()))
)


def get_install_requirements(path):
    content = open(os.path.join(__location__, path)).read()
    requires = [req for req in content.split('\\n') if req != '']
    return requires


setup(
    name='domain-count-spider',
    version='0.0.1',
    description='Scrapy spider ',
    url='https://github.com/ricbartm/domain-count-spider',
    author='Ricardo Bartolome',
    packages=find_packages(exclude=["tests"]),
    install_requires=get_install_requirements('requirements.txt'),
)

#!/usr/bin/env python

from setuptools import setup, find_packages

__version__ = '0.2.2'
__program__ = 'karamel'

setup(
    name=__program__,
    version=__version__,
    description='Karamel is a library that help you build powerful Package Manager based on Git.',
    author='Noel Martignoni',
    author_email='noel@martignoni.fr',
    url='https://gitlab.com/{0}/{0}'.format(__program__),
    scripts=['scripts/{}'.format(__program__)],
    install_requires=['future', 'pyyaml', 'GitPython'],
    packages=find_packages(exclude=['tests*']),
)

# coding: utf-8

from setuptools import setup

from drescher import __version__

setup(
    name='drescher-client',
    version=__version__,
    description='The public Drescher API client',
    packages=['drescher'],
    install_requires=[
        'requests>=2.11.0',
        'six>=1.10.0'
    ]
)

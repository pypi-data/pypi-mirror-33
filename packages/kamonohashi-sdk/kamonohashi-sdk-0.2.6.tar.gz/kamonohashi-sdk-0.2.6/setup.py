# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup

VERSION = '0.2.6'

setup(
    name='kamonohashi-sdk',
    version=VERSION,
    description='KAMONOHASHI SDK for Python',
    long_description='Python client SDK for KAMONOHASHI http://kamonohashi.ai/',
    author='NS Solutions Corporation',
    author_email='kamonohashi-support@jp.nssol.nssmc.com',
    url='https://github.com/KAMONOHASHI/kamonohashi-sdk',
    license='Apache License 2.0',
    packages=find_packages(exclude=('tests', 'docs')),
    install_requires=[
        'requests',
        'tqdm',
        'six',
        'urllib3'
    ],
    dependency_links=[],
    zip_safe=False
)

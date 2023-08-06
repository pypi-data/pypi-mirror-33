#!/usr/bin/env python
from setuptools import find_packages, setup

with open('README.rst') as f:
    readme = f.read()


setup(
    name='Flask-COS',
    version='0.1.1',
    description='腾讯云对象存储的Flask扩展',
    long_description=readme,
    author='codeif',
    author_email='me@codeif.com',
    url='https://github.com/codeif/Flask-COS',
    license='MIT',
    install_requires=['qcos'],
    packages=find_packages(exclude=("tests", "tests.*")),
)

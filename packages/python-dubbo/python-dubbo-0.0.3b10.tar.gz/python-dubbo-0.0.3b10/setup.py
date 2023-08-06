# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name='python-dubbo',
    version='0.0.3-beta10',
    url='https://github.com/RitterHou/python-dubbo',
    author='hourui',
    author_email='hourui@qianmi.com',
    description='Python Dubbo Client.',
    long_description=open('README.md').read(),
    license='Apache License 2.0',
    packages=find_packages(),
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Natural Language :: Chinese (Simplified)',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        'kazoo==2.4.0'
    ],
)

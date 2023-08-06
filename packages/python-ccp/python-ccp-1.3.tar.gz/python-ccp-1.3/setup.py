#!/usr/bin/env python
#-*- coding:utf-8 -*-

from setuptools import setup

with open("README.md") as f:
    long_des = f.read()

setup(name="python-ccp",
      version="1.3",
      author='Pongsakorn Sommalai',
      author_email='bongtrop@gmail.com',
      license='MIT',
      py_modules=['ccp'],
      url='https://github.com/bongtrop/ccp',
      description='copy paste program with clip-server use stdin and stdout',
      long_description=long_des,
      scripts=['ccp.py'],
      install_requires=[
       'requests',
       'docopt_dispatch',
       'pycrypto'
      ],
      entry_points="""
        [console_scripts]
        ccp=ccp:main
      """,
      keywords='copy paste tool'
     )

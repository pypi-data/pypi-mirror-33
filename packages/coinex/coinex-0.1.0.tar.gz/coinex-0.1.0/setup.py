# -*- coding: utf-8 -*-
from setuptools import setup, find_packages
import codecs
import os
import coinex

def read(fname):
    return codecs.open(os.path.join(os.path.dirname(__file__), fname)).read()

long_desc = """

Coinex API
===============

Coinex API. 



Install
--------------

    pip install coinex
    
Upgrade
---------------

    pip install coinex --upgrade
    

Usage
---------

    import coinex
    


"""


setup(
    name='coinex',
    version=coinex.__version__,
    description='Coinex API',
#     long_description=read("READM.rst"),
    long_description = long_desc,
    author='Jimmy',
    author_email='waditu@163.com',
    license='Apache 2.0',
    url='http://tushare.org',
    keywords='Coinex API',
    classifiers=['Development Status :: 4 - Beta',
    'Programming Language :: Python :: 2.6',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.2',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'License :: OSI Approved :: BSD License'],
    packages=find_packages(),
    package_data={'': ['*.csv']},
)
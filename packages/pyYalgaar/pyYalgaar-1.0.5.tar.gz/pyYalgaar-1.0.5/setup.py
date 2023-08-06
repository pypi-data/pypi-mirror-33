#! /usr/bin/env python
#
#  setup.py : Distutils setup script
#  
#  

# Always prefer setuptools over distutils
from setuptools import setup, find_packages
# To use a consistent encoding
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

longdesc = """
pyYalgaar
---------
Yalgaar Python SDK for real-time messaging.

It supports Python 3.4 or newer.


Pip install
-----------

   ::

       pip install pyYalgaar

Getting started with Yalgaar Python SDK
---------------------------------------
`SDK Document <https://www.yalgaar.io/documentation/python-api>`_


Get in touch
------------
If you have any questions, `Contact Us <http://www.yalgaar.io/contact-us>`_


Visit us at
-----------
`www.yalgaar.io <http://www.yalgaar.io>`_
"""
    
setup(
    name='pyYalgaar',
    version='1.0.5',
    description='This is yalgaar python SDK',
    long_description=longdesc,
    url='http://www.yalgaar.io',
    author='Yalgaar',
    author_email='yalgaar@slscorp.com',
    license='MIT',
    platforms = 'Posix; MacOS X; Windows',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    keywords='Connecting to the yalgaar cloud',
    py_modules=['yalgaar', 'client','subscribe', 'publish', 'encrypt'],
    package_data={'': ['api_yalgaar_io.pem']},
    install_requires=['pycryptodome==3.4'],
)

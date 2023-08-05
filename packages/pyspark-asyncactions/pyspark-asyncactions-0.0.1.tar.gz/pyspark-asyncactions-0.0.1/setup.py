import sys
import os
from setuptools import setup, find_packages


install_requires = [] if sys.version_info >= (3, 2) else ["futures"]

setup(
    name='pyspark-asyncactions',
    version='0.0.1',
    packages=find_packages("."),
    url='https://github.com/zero323/pyspark-asyncactions',
    license='Apache 2.0',
    author='zero323',
    author_email='',
    description='A proof of concept asynchronous actions for PySpark using concurent.futures',
    long_description=(open('README.rst').read() if os.path.exists('README.rst')
                        else ''), 
    install_requires=install_requires,
    classifiers=['Programming Language :: Python :: 2',
                 'Programming Language :: Python :: 3',
                 'Development Status :: 3 - Alpha',
                 'License :: OSI Approved :: Apache Software License',
                ]
)

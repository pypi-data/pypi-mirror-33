#!/usr/bin/env python
import setuptools
from distutils.core import setup

setup(name='python-database-rest-logging',
      version='1.0.2',
      description='Python database rest logging',
      author='Marco Mendao',
      author_email='mac.mendao@gmail.com',
      url='http://marcomendao.betacode.tech',
      install_requires=[
            'Flask==0.12',
            'Flask-HTTPAuth==3.2.2',
            'Flask-RESTful==0.3.5',
            'flask-security==1.7.5',
            'flask_cors==3.0.2',
            'pony==0.7.2',
            'graphviz',
            'pymysql',
            'networkx',
            'defusedxml',
            'requests',
            'flask_injector',
            'injector',
      ],
      packages=[
            'python_database_rest_logging',
            'python_database_rest_logging/api',
            'python_database_rest_logging/model',
            'python_database_rest_logging/services'
      ]
)

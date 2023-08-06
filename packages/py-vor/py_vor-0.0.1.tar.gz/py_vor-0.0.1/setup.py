# -*- coding: utf-8 -*-

"""Main setup file"""

from setuptools import setup, find_packages

##########################################
##########################################
##########################################
##########################################

setup(name='py_vor',
      version='0.0.1',
      description='BI automation utilities.',
      url='https://github.com/ksco92/py_vor',
      author='Rodrigo Carvajal',
      author_email='rodrigocf_92@hotmail.com',
      license='MIT',
      packages=find_packages(),
      zip_safe=False,
      install_requires=['boto3',
                        'pandas',
                        'pyodbc',
                        'pymysql',
                        'pg8000'
                        ]
      )

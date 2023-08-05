# -*- coding: utf-8 -*-
"""
Created on Fri May 18 13:56:46 2018

@author: yili.peng
"""


from setuptools import setup

def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='alpha_factory'
      ,version='0.1.5'
      ,description='generate alpha factors'
      ,long_description=readme()
      ,keywords='quant factor model'
      ,lisence='MIT'
      ,author='Yili Peng'
      ,author_email='yili.peng@outlook.com'
      ,packages=['alpha_factory']
      ,install_requires=[
          'RNWS',
      ]
      ,package_data={
        'alpha_factory': ['data/functions.csv'],
        }
      ,zip_safe=False)
#!/usr/bin/env python

from distutils.core import setup

setup(name='ostrich-json',
      version='1.0.3',
      description='No exception json package, just log',
      long_description=open('README.txt').read(),
      author='Ma HaoYang',
      author_email='martinlord@foxmail.com',
      url='https://github.com/mahaoyang/spider-tool/tree/master/ostrich_json',
      packages=['ostrich_json'],
      license='LICENSE.txt',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Operating System :: OS Independent',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Programming Language :: Python',
          'Programming Language :: Python :: Implementation',
          'Programming Language :: Python :: 3',
          'Topic :: Software Development :: Libraries'
      ],
      )

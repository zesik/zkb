#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
zkb
~~~

ZKB, a static blog generator.

:Copyright: Copyright 2014 Yang LIU <zesikliu@gmail.com>
:License: BSD, see LICENSE for details.
"""

from setuptools import setup, find_packages

setup(name='zkb',
      version=__import__('zkb').__version__,
      description='A static blog generator',
      url='http://zesik.me/',
      author='Yang LIU',
      author_email='zesikliu@gmail.com',
      license='BSD',
      packages=find_packages(exclude=['test', 'test.*']),
      include_package_data=True,
      install_requires=[
          'pyyaml',
          'markdown',
          'pygments',
          'jinja2',
          'python-slugify'],
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Environment :: Console',
          'Intended Audience :: End Users/Desktop',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: BSD License',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
          'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary'])

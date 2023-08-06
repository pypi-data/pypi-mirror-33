#!/usr/bin/env python3

from distutils.core import setup
setup(name='curses-util',
      version='0.0.11',
      author='Raheman Vaiya',
      author_email='r.vaiya@gmail.com',
      url='http://gitlab.com/rvaiya/curses-utils',
      packages=['curses_util'],
      keywords='console menu curses simple',
      long_description=open('README.rst').read(),
      classifiers=[
          'Programming Language :: Python :: 3',
          'Development Status :: 3 - Alpha'
      ]
)

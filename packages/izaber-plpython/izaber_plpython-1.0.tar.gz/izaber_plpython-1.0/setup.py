#!/usr/bin/python

from setuptools import setup

setup(name='izaber_plpython',
      version='1.0',
      description='Base load point for iZaber plpython',
      url = 'https://github.com/zabertech/izaber-plpython',
      download_url = 'https://github.com/zabertech/python-plpython/archive/1.0.tar.gz',
      author='Aki Mimoto',
      author_email='aki+izaber@zaber.com',
      license='MIT',
      packages=['izaber_plpython'],
      scripts=[],
      install_requires=[
          'izaber',
      ],
      dependency_links=[],
      zip_safe=False)


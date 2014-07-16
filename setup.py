#!/usr/bin/env python

from setuptools import setup, find_packages

requirements = open('requirements.txt').read().splitlines()
setup(name='Linkitup',
      version='2.2',
      description='Linkitup Web-based Dashboard for Enriching Research Data',
      author='Rinke Hoekstra, Marat Charlaganov',
      author_email='rinke.hoekstra@vu.nl',
      url='http://github.com/Data2Semantics/linkitup',
      package_data={'linkitup': ['plugins.yaml', 'templates/*.html',
                  'templates/*.query', 'templates/*.js', 'static/js/*.js',
                  'static/css/*.css', 'static/css/*.png', 'static/img/*.png',
                  'static/js/vendor/*.js', 'migrations/*.*',
                  'migrations/versions/*']},
      packages=find_packages(),
      scripts=['manage.py'],
      # long_description=open('README.txt').read(),
      install_requires=requirements)

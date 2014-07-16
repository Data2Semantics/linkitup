#!/usr/bin/env python

from setuptools import setup, find_packages

requirements = open('requirements.txt').read().splitlines()
setup(name='Linkitup',
      version='2.1',
      description='Linkitup Web-based Dashboard for Enriching Research Data',
      author='Rinke Hoekstra, Marat Charlaganov',
      author_email='rinke.hoekstra@vu.nl',
      url='http://github.com/Data2Semantics/linkitup',
      package_data={'app':['templates/*.html','templates/*.query','templates/*.js','static/js/*.js','static/css/*.css','static/css/*.png','static/img/*.png','static/js/vendor/*.js']},
      packages=find_packages(),
      scripts=['manage.py'],
      # long_description=open('README.txt').read(),
      install_requires=requirements)

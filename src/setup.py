#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='Linkitup',
      version='1.1',
      description='Linkitup Web-based Dashboard for Enriching Research Data',
      author='Rinke Hoekstra, Marat Charlaganov',
      author_email='rinke.hoekstra@vu.nl',
      url='http://github.com/Data2Semantics/linkitup',
      package_data={'app':['templates/*.html','templates/*.query','templates/*.js','static/js/*.js','static/css/*.css','static/css/*.png','static/img/*.png','static/js/vendor/*.js']},
      packages=find_packages(),
      scripts=['config.py','db_create.py','run.py'],
      long_description=open('README.txt').read(),
      install_requires=['flask', 'flask-login', 'flask-openid','sqlalchemy','flask-sqlalchemy','sqlalchemy-migrate',
      'flask-wtf','rdflib > 4.0','SPARQLWrapper','beautifulsoup4','pdfminer','requests','pyyaml'])


# import os, subprocess, sys
# 
# subprocess.call(['pip', 'install', 'flask'])
# subprocess.call(['pip', 'install', 'flask-login'])
# subprocess.call(['pip', 'install', 'flask-openid'])
# if sys.platform == 'win32':
#     subprocess.call(['pip', 'install', '--no-deps', 'lamson', 'chardet', 'flask-mail'])
# else:
#     subprocess.call(['pip', 'install', 'flask-mail'])
# subprocess.call(['pip', 'install', 'sqlalchemy==0.7.9'])
# subprocess.call(['pip', 'install', 'flask-sqlalchemy'])
# subprocess.call(['pip', 'install', 'sqlalchemy-migrate'])
# subprocess.call(['pip', 'install', 'flask-whooshalchemy'])
# subprocess.call(['pip', 'install', 'flask-wtf'])
# subprocess.call(['pip', 'install', 'flask-babel'])
# subprocess.call(['pip', 'install', 'flup'])
# # subprocess.call(['pip', 'install', 'flask-kvsession'])
# subprocess.call(['pip', 'install', 'flask-uploads'])
# subprocess.call(['pip', 'install', 'rdflib', '--upgrade'])
# subprocess.call(['pip', 'install', 'SPARQLWrapper'])
# subprocess.call(['pip', 'install', 'beautifulsoup4'])
# subprocess.call(['pip', 'install', 'pdfminer'])
# subprocess.call(['pip', 'install', 'requests'])

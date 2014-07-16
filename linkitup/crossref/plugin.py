"""

Module:	   plugin.py
Author:	   Rinke Hoekstra
Created:   2 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
# -*- coding: utf-8 -*-


from flask import render_template, request, make_response, jsonify
from flask.ext.login import login_required

from werkzeug.datastructures import FileStorage
from tempfile import NamedTemporaryFile

import json
import requests
import urllib
from extract import extract_references
import re
import cStringIO

from pprint import pprint

from linkitup import app





@app.route('/crossref', methods=['POST'])
@login_required
def link_to_DOI():
	# Retrieve the article from the post
	article = request.get_json()
	article_id = article['article_id']


	# Only applicable to PDF files
	files = [f for f in article['files'] if f['mime_type'] == 'application/pdf']


	if len(files) > 0:
		return render_template('crossref.html',
							   title = 'Crossref',
							   files = files, 
							   article_id = article_id)
	else :		  
		return render_template('message.html',
							   type = 'error',
							   text = 'This dataset does not contain any PDF files')


@app.route('/crossref/upload', methods = ['POST'])
@login_required
def upload_to_crossref():
	# Retrieve the file from the post
	figshare_file = request.get_json()
	
	file_name = figshare_file['name'].replace('-','_')
	file_id = figshare_file['id']
	
	url = "http://files.figshare.com/{}/{}".format(file_id, file_name)
	
	app.logger.debug("Getting file from {}".format(url))
	r = requests.get(url)
	
	if r.ok :
		app.logger.debug("Response ok")
		
		tempfile = open('/tmp/{}'.format(file_name),'w+b')
		tempfile.write(r.content)
		tempfile.close()
		
		figshare_file['tempfile'] =  tempfile.name

		result = {'success': True, 'file': figshare_file }
		return jsonify(result)
	
	else :
		app.logger.debug("Response not ok")
		app.logger.debug(r)
		app.logger.debug(r.text)
		result = {'success': False}
		return jsonify(result)


@app.route('/crossref/extract', methods=['POST'])
@login_required
def get_file_and_extract():
	figshare_file = request.get_json()
	
	# TODO: Use a web-based PDF extraction service instead
	
	# Use the reference extraction function from the bundled extract.py script
	references = extract_references(figshare_file['tempfile'])
	
	result = {'success': True, 'references': references}
	return jsonify(result)

@app.route('/crossref/match', methods = ['POST'])
@login_required
def match_references():
	# CrossRef search http://crossref.org/sigg/sigg/FindWorks?version=1&access=API_KEY&format=json&op=OR&expression=allen+renear
	request_data = request.get_json()

	reference = request_data['reference']
	figshare_file = request_data['file']
	file_id = figshare_file['id']
	
	data = {'version': 1,
			'access': 'API_KEY',
			'format': 'json',
			'op': 'OR',
			'expression': reference['text']
			}
	
	r = requests.get('http://crossref.org/sigg/sigg/FindWorks', params=data)
	
	app.logger.debug(r.text)
	
	try :
		results = json.loads(r.text)
		
		
		urls = []
		for r in results[0:3]:
			uri = 'http://dx.doi.org/{}'.format(r['doi'])
			
			short = re.sub('\.|/','_',r['doi'])
			
			
			urls.append({'type': 'reference', 'uri': uri, 'web': uri, 'show': r['fullCitation'], 'short': short, 'original': 'figshare_{}'.format(file_id)})
	except Exception as e:
		urls = []
		app.logger.warning("No results returned")
		app.logger.debug(e.message)	   
	
	if urls == []:
		urls = None
	
	return jsonify({'title':'Crossref References','urls': urls})
	
	
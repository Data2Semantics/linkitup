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
from flaskext.uploads import UploadSet

from werkzeug.datastructures import FileStorage
from tempfile import NamedTemporaryFile

import json
import requests
import urllib
from extract import extract_references
import re
import cStringIO

from pprint import pprint

from app import app, pdfs




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


@app.route('/crossref/upload/<article_id>/<file_id>/<file_name>', methods = ['GET'])
@login_required
def upload_to_crossref(article_id, file_id, file_name):
	app.logger.debug("Article {}, File {} ({})".format(article_id, file_name, file_id))
	
	app.logger.debug("Replacing hyphens with underscores in filename")
	file_name = file_name.replace('-','_')
	
	url = "http://files.figshare.com/{}/{}".format(file_id, file_name)
	
	app.logger.debug("Getting file from {}".format(url))
	r = requests.get(url)
	

	
	if r.ok :
		app.logger.debug("Response ok")
		
		tempfile = open('/tmp/{}'.format(file_name),'w+b')
		tempfile.write(r.content)
		tempfile.close()
		
		app.logger.debug('upload: tempfile {}'.format(tempfile.name))

		
		result = {
			"name":"{}.pdf".format(file_id),
			"tempfile": tempfile.name
		}
		app.logger.debug(result)
		
		return jsonify(result)
	
	else :
		app.logger.debug("Response not ok")
		app.logger.debug(r)
		app.logger.debug(r.text)
		result = {'name': 'Something went wrong ...'}
		return jsonify(result)


@app.route('/crossref/extract/<article_id>/<file_id>/<tempfile>')
@login_required
def get_file_and_extract(article_id, file_id, tempfile):

	app.logger.debug('extract: files_file_id (tempfile)', pdfs.path(tempfile))
	
	# TODO: Use a web-based PDF extraction service instead
	
	# Use the reference extraction function from the bundled extract.py script
	references = extract_references(pdfs.path(tempfile))
		
	return render_template('references.html',
						   article_id = article_id, 
						   file_id = file_id, 
						   references = references )

@app.route('/crossref/match/<article_id>/<file_id>', methods = ['GET'])
@login_required
def match_references(article_id, file_id):
	# CrossRef search http://crossref.org/sigg/sigg/FindWorks?version=1&access=API_KEY&format=json&op=OR&expression=allen+renear
	text = urllib.unquote(request.args.get('text'))

	data = {'version': 1,
			'access': 'API_KEY',
			'format': 'json',
			'op': 'OR',
			'expression': text
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
	
	return render_template('crossref_urls.html',
						   urls = urls)
	
	
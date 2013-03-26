"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   2 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
# -*- coding: utf-8 -*-


from flask import render_template, session, request, make_response
from flask.ext.login import login_required
from flaskext.uploads import UploadSet

import json
import requests
import urllib
from extract import extract_references
import re

from pprint import pprint

from app import app, pdfs




@app.route('/crossref/<article_id>')
@login_required
def link_to_DOI(article_id):
    items = session.get('items',[])
    
    
    i = items[article_id]

    # Only applicable to PDF files
    files = [f for f in i['files'] if f['mime_type'] == 'application/pdf']
            
    if len(files) > 0:
        return render_template('crossref.html',
                               title = 'Crossref',
                               files = files, 
                               article_id = article_id)
    else :        
        return render_template('message.html',
                               type = 'error',
                               text = 'This dataset does not contain any PDF files')


@app.route('/crossref/upload/<article_id>/<file_id>', methods = ['POST'])
@login_required
def upload_to_crossref(article_id, file_id):
    app.logger.debug("Article {}, File {}".format(article_id, file_id))
    
    app.logger.debug(pprint(request.files))
    
    if 'files[]' in request.files :
        result = [{'name': request.files['files[]'].name}]
        
        app.logger.debug(request.files['files[]'])
        
        tempfile = pdfs.save(request.files['files[]'])

        app.logger.debug('upload: tempfile {}'.format(tempfile))
        
        session.setdefault('files',{})[file_id] = tempfile
        session.modified = True
        
        app.logger.debug('upload: files {}'.format(session['files']))
        
        result = [  {
            "name":"{}.pdf".format(file_id)
        }]
        app.logger.debug(result)
        
        return json.dumps(result)
    
    else :
        result = [{'name': 'Something went wrong ...'}]
        return make_response(json.dumps(result), mimetype="application/json")


@app.route('/crossref/extract/<article_id>/<file_id>')
@login_required
def get_file_and_extract(article_id, file_id):
    app.logger.debug('extract: files', session.get('files'))

    tempfile = session['files'][file_id]
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
            
            
            urls.append({'type': 'reference', 'uri': uri, 'web': uri, 'show': r['fullCitation'], 'short': short, 'original': 'FS{}'.format(file_id)})
    except Exception as e:
        urls = []
        app.logger.warning("No results returned")
        app.logger.debug(e.message)    
    
    session.setdefault(article_id,[]).extend(urls)
    session.modified = True
    
    if urls == []:
        urls = None
    
    return render_template('crossref_urls.html',
                           urls = urls)
    
    
"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   2 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""

from flask import render_template, session
from flask.ext.login import login_required

import requests
import json
import re
from pprint import pprint

from app import app

_known_vocabularies = ['SciValFunders']

@app.route('/ldr/<article_id>')
@login_required
def link_to_ldr(article_id):
    app.logger.debug("Running LDR plugin for article {}".format(article_id))
    items = session['items']
    
    urls = []
    
    i = items[article_id]
    
      
    tags_and_categories = i['tags'] + i['categories']
    
    for t in tags_and_categories:
        for v in _known_vocabularies :
            data = {'conceptName': t['name']}
            
            request_uri = 'http://data.elsevier.com/content/vocabulary/concept/{}'.format(v)
            
            r = requests.get(request_uri, params=data)
            
            concepts = json.loads(r.text)
            
            if len(concepts)>0 :
                for c in concepts['concepts'] :
                    label = c['prefLabel']['label']['literalForm']['value']
                    uri = c['id']
                    
                    short = re.sub(' |/|\|\.|-','_',label)
                    
                    urls.append({'type':'mapping', 'uri': uri, 'web': uri, 'show': label, 'short': short, 'original': label})
            

    session.setdefault(article_id,[]).extend(urls)
    session.modified = True
    
    if urls == [] :
        urls = None 
        
    return render_template('urls.html',
                           article_id = article_id, 
                           results = [{'title':'Linked Data Repository','urls': urls}])  
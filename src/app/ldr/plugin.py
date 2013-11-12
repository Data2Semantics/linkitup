"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   2 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""

from flask import render_template, request, jsonify
from flask.ext.login import login_required

import requests
import json
import re
from pprint import pprint

from app import app

from app.util.baseplugin import plugin
from app.util.provenance import provenance

_known_vocabularies = ['SciValFunders']

@app.route('/ldr', methods=['POST'])
@login_required
@plugin(fields=[('tags','id','name'),('categories','id','name')], link='mapping')
@provenance()
def link_to_ldr(*args, **kwargs):
    # Retrieve the article from the post
    article_id = kwargs['article']['id']
    
    app.logger.debug("Running LDR plugin for article {}".format(article_id))
    
    urls = {}
    
    tags_and_categories = kwargs['inputs']
    
    for t in tags_and_categories:
        
        original_qname = "figshare_{}".format(t['id'])
        
        for v in _known_vocabularies :
            data = {'conceptName': t['label']}
            
            request_uri = 'http://data.elsevier.com/content/vocabulary/concept/{}'.format(v)
            
            r = requests.get(request_uri, params=data)
            
            concepts = json.loads(r.text)
            
            if len(concepts)>0 :
                for c in concepts['concepts'] :
                    label = c['prefLabel']['label']['literalForm']['value']
                    uri = c['id']
                    
                    short = re.sub(' |/|\|\.|-','_',label)
                    
                    urls[uri] = {'type':'mapping', 'uri': uri, 'web': uri, 'show': label, 'short': short, 'original': original_qname}
             
        
    return urls 
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

_known_vocabularies = ['SciValFunders']

@app.route('/ldr', methods=['POST'])
@login_required
def link_to_ldr():
    # Retrieve the article from the post
    article = request.get_json()
    article_id = article['article_id']
    
    app.logger.debug("Running LDR plugin for article {}".format(article_id))
    
    urls = []
    
    
      
    tags_and_categories = article['tags'] + article['categories']
    
    for t in tags_and_categories:
        
        original_qname = "figshare_{}".format(t['id'])
        
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
                    
                    urls.append({'type':'mapping', 'uri': uri, 'web': uri, 'show': label, 'short': short, 'original': original_qname})
            
    if urls == [] :
        urls = None 
        
    return jsonify({'title':'Linked Data Repository','urls': urls})  
"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   2 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""

from django.shortcuts import render_to_response
import requests
import json
import re
from pprint import pprint


_known_vocabularies = ['SciValFunders']

def linkup(request, article_id):
    items = request.session['items']
    
    urls = []
    
    
    for i in items :
        if str(i['article_id']) == str(article_id):        
            tags_and_categories = i['tags'] + i['categories']
            
            for t in tags_and_categories:
                for v in _known_vocabularies :
                    data = {'conceptName': t['name']}
                    
                    request_uri = 'http://data.elsevier.com/content/vocabulary/concept/{}'.format(v)
                    
                    r = requests.get(request_uri, params=data)
                    
                    concepts = json.loads(r.text)
                
                    
                    if len(concepts)>0 :
                        for c in concepts['concepts'] :
                            pprint(c)
                            label = c['prefLabel']['label']['literalForm']['value']
                            uri = c['id']
                            
                            short = re.sub(' |/|\|\.|-','_',label)
                            
                            urls.append({'type':'mapping', 'uri': uri, 'web': uri, 'show': label, 'short': short, 'original': label})
                    
    
    request.session.setdefault(article_id,[]).extend(urls)
    request.session.modified = True
    
    if urls == [] :
        urls = None 
        
    return render_to_response('urls.html',{'article_id': article_id, 'results':[{'title':'Linked Data Repository','urls': urls}]})  
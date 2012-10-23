'''
Created on Oct 23, 2012

@author: hoekstra
'''


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
            print article_id
            
            tags_and_categories = i['tags'] + i['categories']
            
            for t in tags_and_categories:
                print t['name']
                for v in _known_vocabularies :
                    print v
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
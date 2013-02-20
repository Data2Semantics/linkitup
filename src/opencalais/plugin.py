"""
Module: opencalais.plugin
Author:  hoekstra
Created: Feb 6, 2013


Copyright (c) 2013, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""

from django.shortcuts import render_to_response
import requests
import json
import re
from pprint import pprint


def linkup(request, article_id):
    items = request.session['items']
    
    urls = []
    
    
    i = items[article_id]    

                    
# urls.append({'type':'mapping', 'uri': uri, 'web': uri, 'show': label, 'short': short, 'original': label})
                    
    
    request.session.setdefault(article_id,[]).extend(urls)
    request.session.modified = True
    
    if urls == [] :
        urls = None 
        
    return render_to_response('urls.html',{'article_id': article_id, 'results':[{'title':'Linked Data Repository','urls': urls}]})  
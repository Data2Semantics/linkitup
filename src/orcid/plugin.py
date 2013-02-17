"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   24 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""

from django.shortcuts import render_to_response
import requests
import json
import re
import urllib
from pprint import pprint



orcid_url = 'http://pub.orcid.org/'
credit_search_url = orcid_url + 'search/orcid-bio/?q=text:'

def linkup(request, article_id):
    items = request.session['items']
    
    urls = []
    
    
    i = items[article_id]

    authors = i['authors']
    
    for a in authors:
        a_id = a['id']
        a_qname = 'FS{}'.format(a_id)
        full_name = a['full_name'].strip()

        request_uri = credit_search_url + urllib.quote_plus(full_name) + "&rows=3"
        
        headers = {'Accept': 'application/orcid+json'}
        
        r = requests.get(request_uri, headers=headers)

        search_results = json.loads(r.content)

        if len(search_results) >0 :
            for sr in search_results['orcid-search-results']['orcid-search-result']:
                try :
                    orcid = sr['orcid-profile']['orcid']['value']
                    
                    score_double = sr['relevancy-score']['value']
                 
                    
                    score = 'score: {0:.2g}'.format(score_double)
                    
                    details = sr['orcid-profile']['orcid-bio']['personal-details']
                    
                    if 'credit-name' in details:
                        name = details['credit-name']['value']
                    else :
                        name = "{} {}".format(details['given-names']['value'].encode('utf-8'),details['family-name']['value'].encode('utf-8'))
                        
                    if score_double < 2 :
#                        print "Score {} for {} is below 2, not including it in results.".format(sr['relevancy-score']['value'], name)
                        continue   
                    
                    uri = "http://orcid.org/{}".format(orcid)
                    
                    short = re.sub(' |/|\|\.|-','_',orcid)
                
                    urls.append({'type':'mapping', 'uri': uri, 'web': uri, 'show': name, 'short': short, 'original': a_qname, 'extra': orcid, 'subscript': score})
                except Exception as e :
                    return render_to_response('message.html',{'type': 'error', 'text': e.message })
                    

    print "eight"   
    request.session.setdefault(article_id,[]).extend(urls)
    request.session.modified = True
    
    if urls == [] :
        urls = None 
    
    print "nine"
    return render_to_response('urls.html',{'article_id': article_id, 'results':[{'title':'ORCID','urls': urls}]})  
'''
Created on Oct 24, 2012

@author: hoekstra
'''
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
    
    
    for i in items :
        if str(i['article_id']) == str(article_id):
            print article_id
            
            authors = i['authors']
            
            
            for a in authors:
                a_id = a['id']
                a_qname = 'FS{}'.format(a_id)
                full_name = a['full_name'].strip()

                print full_name
                request_uri = credit_search_url + urllib.quote_plus(full_name) + "&rows=3"
                
                print request_uri
                headers = {'Accept': 'application/orcid+json'}
                
                r = requests.get(request_uri, headers=headers)

                search_results = json.loads(r.content)

                if len(search_results) >0 :
                    for sr in search_results['orcid-search-results']['orcid-search-result']:
                        orcid = sr['orcid-profile']['orcid']['value']
                        
                        score_double = sr['relevancy-score']['value']
                        
                        
                        score = 'score: {0:.2g}'.format(sr['relevancy-score']['value'])
                        
                        details = sr['orcid-profile']['orcid-bio']['personal-details']
                        
                        if 'credit-name' in details:
                            name = details['credit-name']['value']
                        else :
                            name = "{} {}".format(details['given-names']['value'],details['family-name']['value'])
                        
                        if score_double < 2 :
                            print "Score {} for {} is below 2, not including it in results.".format(sr['relevancy-score']['value'], name)
                            continue
                            
                        uri = "http://orcid.org/{}".format(orcid)
                        
                        short = re.sub(' |/|\|\.|-','_',orcid)
                    
                        
                        print uri, name
                        urls.append({'type':'mapping', 'uri': uri, 'web': uri, 'show': name, 'short': short, 'original': a_qname, 'extra': orcid, 'subscript': score})
                    
    request.session.setdefault(article_id,[]).extend(urls)
    request.session.modified = True
    
    if urls == [] :
        urls = None 
        
    return render_to_response('urls.html',{'article_id': article_id, 'results':[{'title':'ORCID','urls': urls}]})  
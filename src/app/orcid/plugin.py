"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   24 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""

from flask import render_template, session
from flask.ext.login import login_required

import requests
import json
import re
import urllib
from pprint import pprint

from app import app



orcid_url = 'http://pub.orcid.org/'
credit_search_url = orcid_url + 'search/orcid-bio/?q=text:'

@app.route('/orcid/<article_id>')
@login_required
def link_to_orcid(article_id):
    items = session['items']
    
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
                    elif 'given-names' in details and 'family-name' in details :
                        name = "{} {}".format(details['given-names']['value'].encode('utf-8'),details['family-name']['value'].encode('utf-8'))
                    elif 'other-name' in details :
                        name = details['other-name']['value'].encode('utf-8')
                    else :
                        app.logger.debug('No name found in ORCID entry')
                        continue
                        
                    if score_double < 2 :
                        app.logger.debug("Score {} for {} is below 2, not including it in results.".format(sr['relevancy-score']['value'], name))
                        continue   
                    
                    uri = "http://orcid.org/{}".format(orcid)
                    
                    short = re.sub(' |/|\|\.|-','_',orcid)
                
                    urls.append({'type':'mapping', 'uri': uri, 'web': uri, 'show': name, 'short': short, 'original': a_qname, 'extra': orcid, 'subscript': score})
                except Exception as e :
                    app.logger.debug("Exception in accessing ORCID entry: {}\n{}".format(e.message, pprint(sr)))
                    return render_template('message.html',
                                           type = 'error', 
                                           text = e.message )
                    

    session.setdefault(article_id,[]).extend(urls)
    session.modified = True
    
    if urls == [] :
        urls = None 
    
    return render_template('urls.html',
                           article_id = article_id, 
                           results = [{'title':'ORCID','urls': urls}] )  
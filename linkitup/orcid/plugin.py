"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   24 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""

from flask.ext.login import login_required

import requests
import json
import re
import urllib
from pprint import pprint
import traceback

from linkitup import app

from linkitup.util.baseplugin import plugin
from linkitup.util.provenance import provenance


orcid_url = 'http://pub.orcid.org/'
credit_search_url = orcid_url + 'search/orcid-bio/?q=text:'

@app.route('/orcid', methods=['POST'])
@login_required
@plugin(fields=[('authors','id','full_name')], link='mapping')
@provenance()
def link_to_orcid(*args,**kwargs):
    # Retrieve the article from the wrapper
    article_id = kwargs['article']['id']
    
    app.logger.debug("Running ORCID plugin for article {}".format(article_id))
    
    urls = {}
    
    authors = kwargs['inputs']
    
    for a in authors:
        a_id = a['id']
        full_name = a['label']

        request_uri = credit_search_url + urllib.quote_plus(full_name) + "&rows=3"
        
        headers = {'Accept': 'application/orcid+json'}
        
        r = requests.get(request_uri, headers=headers)

        search_results = json.loads(r.content)

        if len(search_results) >0 :
            for sr in search_results['orcid-search-results']['orcid-search-result']:
                app.logger.debug(sr)
                try :
                    orcid_uri = sr['orcid-profile']['orcid-identifier']['uri']
                    orcid_path = sr['orcid-profile']['orcid-identifier']['path']
                    score_double = sr['relevancy-score']['value']
                 
                    
                    score = 'score: {0:.2g}'.format(score_double)
                    
                    details = sr['orcid-profile']['orcid-bio']['personal-details']
                    
                    if 'credit-name' in details:
                        name = details['credit-name']['value'].encode('utf-8')
                    elif 'given-names' in details and 'family-name' in details :
                        name = "{} {}".format(details['given-names']['value'].encode('utf-8'),details['family-name']['value'].encode('utf-8'))
                    elif 'other-name' in details :
                        name = details['other-name']['value'].encode('utf-8')
                    else :
                        app.logger.debug('No name found in ORCID entry')
                        continue
                        
                    if score_double < 0.7 :
                        app.logger.debug("Score {} for {} is below 0.7, not including it in results.".format(sr['relevancy-score']['value'], name))
                        continue   
                    
                    short = re.sub(' |/|\|\.|-','_',orcid_path)
                
                    urls[orcid_uri] = {'type':'mapping', 'uri': orcid_uri, 'web': orcid_uri, 'show': name, 'short': short, 'original': a_id, 'extra': orcid_path, 'subscript': score}
                except Exception as e :
                    app.logger.debug("Exception in accessing ORCID entry: {}\n{}".format(e.message, pprint(sr)))
                    app.logger.debug(traceback.format_exc())
                    return {'error': e.message }
    return urls

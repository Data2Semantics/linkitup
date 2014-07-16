'''
Created on 4 Nov 2013

@author: cmarat
'''

from flask.ext.login import login_required

import requests

from linkitup import app
from linkitup.util.baseplugin import plugin
from linkitup.util.provenance import provenance

SAMEAS_URL = "http://sameas.org/json"


@app.route('/sameas', methods=['POST'])
@login_required
@plugin(fields=[('links','id','link')], link='mapping')
@provenance()
def link_to_sameas(*args, **kwargs):
    # Retrieve the article from the wrapper
    article_id = kwargs['article']['id']
    app.logger.debug("Running sameAs.org plugin for article {}".format(article_id))
    
    # Get article links
    match_items = kwargs['inputs']
    matches = {}

    for item in match_items:
        item_link = item['label']
        original_qname = "figshare_{}".format(item['id'])
        
        # Query sameas.org
        response = requests.get(SAMEAS_URL, params={'uri': item_link})
        hits = response.json()

        # Make a list of all links returned by sameas.org
        sameas_links = [uri for h in hits for uri in h['duplicates'] if uri != item_link]
        
        for uri in sameas_links:
        
            # Create the match dictionary
            match = {'type':    'mapping',
                     'uri':     uri,
                     'web':     uri,
                     'show':    uri,
                     'original':original_qname}
        
            # Append it to all matches
            matches[uri] = match

    # Return the matches
    return matches

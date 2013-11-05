'''
Created on 4 Nov 2013

@author: cmarat
'''

from flask import request, jsonify
from flask.ext.login import login_required

import requests

from app import app

SAMEAS_URL = "http://sameas.org/json"


@app.route('/sameas', methods=['POST'])
@login_required
def link_to_sameas():
    # Retrieve the article from the post
    article = request.get_json()
    article_id = article['article_id']
    
    app.logger.debug("Running sameAs.org plugin for article {}".format(article_id))
    
    # Get article links
    match_items = article['links']
    match_items.append({u'link': u'http://dbpedia.org/resource/Resource_Description_Framework', u'id': 9999})

    matches = {}

    for item in match_items:
        
        item_link = item['link']
        original_qname = "figshare_{}".format(item['id'])
        
        # Query sameas.org
        response = requests.get(SAMEAS_URL, params={'uri': item_link})
        hits = response.json()

        # Make a list of all links returned by sameas.org
        sameas_links = [uri for h in hits for uri in h['duplicates'] if uri != item_link]
        
        for uri in sameas_links:
        
            # Create the match dictionary
            match = {'type':    "mapping",
                     'uri':     uri,
                     'web':     uri,
                     'show':    uri,
                     'original':original_qname}
        
            # Append it to all matches
            matches[uri] = match

    if matches == {} :
        matches = None
    
    # Return the matches
    return jsonify({'title':'sameAs.org links','urls': matches})

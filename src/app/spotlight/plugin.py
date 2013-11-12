'''
Created on 6 Nov 2013

@author: cmarat
'''

from flask import request, jsonify
from flask.ext.login import login_required

from nltk import clean_html
import requests

from app import app

SPOTLIGHT_URL = 'http://spotlight.dbpedia.org/rest/annotate'


@app.route('/spotlight', methods=['POST'])
@login_required
def link_to_spotlight():
    # Retrieve the article from the post
    article = request.get_json()
    article_id = article['article_id']
    original_qname = "figshare_{}".format(article_id)
    
    app.logger.debug("Running DBpedia Spotlight plugin for article {}".format(article_id))
    
    # Get article description
    description = clean_html(article['description'])
    confidence = 0.2
    response = requests.post(   SPOTLIGHT_URL,
                                data={'text': description, 'confidence': confidence},
                                headers={'Accept': 'application/json'})
    resources = response.json().get('Resources', [])

    matches = {}

    for resource in resources:
        dbpedia_uri = resource['@URI']
        score = 'score: {}'.format(resource['@similarityScore'][:4])
        types = " ,".join(resource['@types'].split(',')[:5])
        if types == '':
            types = None

        # offset = int(resource['@offset'])
        # fragment = "...{}...".format(description[offset-30 : offset+30])

        match = {'type': "reference",
                 'uri': dbpedia_uri,
                 'web': dbpedia_uri,
                 'show': dbpedia_uri,
                 'extra': types,
                 'subscript': score,
                 # 'description': fragment,
                 'original': original_qname}
        
            # Append it to all matches
        matches[dbpedia_uri] = match

    if matches == {} :
        matches = None
    
    # Return the matches
    return jsonify({'title':'DBpedia Spotlight','urls': matches})

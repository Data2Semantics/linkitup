'''
Created on 6 Nov 2013

@author: cmarat
'''

from flask import request
from flask.ext.login import login_required
import requests
from bs4 import BeautifulSoup

from linkitup import app
from linkitup.util.baseplugin import plugin
from linkitup.util.provenance import provenance

SPOTLIGHT_URL = 'http://spotlight.dbpedia.org/rest/annotate'
SPOTLIGHT_CONFIDENCE = 0.2
SIMILARITY_CUTOUT = 0.1

@app.route('/spotlight', methods=['POST'])
@login_required
@plugin(fields=[('tags','id','name'),('categories','id','name')], link='link')
@provenance()
def link_to_spotlight(*args, **kwargs):

    article_id = kwargs['article']['id']

    app.logger.debug("Running DBpedia Spotlight plugin for article {}".format(article_id))

    match_items = kwargs['inputs']
    labels = ", ".join([item['label'] for item in kwargs['inputs'] + [kwargs['article']]])
    
    # Get article description, the wrapper does not provide it yet
    article = request.get_json()
    soup = BeautifulSoup(article['description'])
    description = soup.get_text()

    # Query text consists of article title, description, tags, and categories
    # app.logger.debug("Spotlight query text:\n {}".format(text))

    response = requests.post(   SPOTLIGHT_URL,
                                data={'text': text, 'confidence': SPOTLIGHT_CONFIDENCE},
                                headers={'Accept': 'application/json'})
    text = u"{}\n\n{}".format(description, labels)
    resources = response.json().get('Resources', [])

    matches = {}

    for resource in resources:
        dbpedia_uri = resource['@URI']
        similarity_score = float(resource['@similarityScore'])
        if similarity_score < SIMILARITY_CUTOUT:
            continue
        score = 'score: {:.2g}'.format(similarity_score)

        types = " ,".join(resource['@types'].split(','))
        if types == '':
            types = None

        match = {'type': 'link',
                 'uri': dbpedia_uri,
                 'web': dbpedia_uri,
                 'show': dbpedia_uri,
                 'extra': types,
                 'subscript': score,
                 'original': article_id}
        
            # Append it to all matches
        matches[dbpedia_uri] = match

    # Return the matches
    return matches

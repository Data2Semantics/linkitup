'''
Created on 6 Nov 2013

@author: cmarat
'''

from flask import request
from flask.ext.login import login_required
import requests
from bs4 import BeautifulSoup

from linkitup import app
from linkitup.util import wikipedia_url
from linkitup.util.baseplugin import plugin
from linkitup.util.provenance import provenance
from linkitup.util.preflabel import label

SPOTLIGHT_URL = 'http://spotlight.dbpedia.org/rest/annotate'
SPOTLIGHT_CONFIDENCE = 0.2
SIMILARITY_CUTOUT = 0.1


@app.route('/spotlight', methods=['POST'])
@login_required
@plugin(fields=[('tags', 'id', 'name'), ('categories', 'id', 'name')],
        link='link')
@provenance()
def link_to_spotlight(*args, **kwargs):

    article_id = kwargs['article']['id']

    app.logger.debug("Running DBpedia Spotlight plugin for article {}".format(
        article_id))

    labels = ", ".join([item['label'] for item in kwargs['inputs']
                        + [kwargs['article']]])

    # Get article description, the wrapper does not provide it yet
    article = request.get_json()
    soup = BeautifulSoup(article['description'])
    description = soup.get_text()

    # Query text consists of article title, description, tags, and categories
    text = u"{}\n\n{}".format(description, labels)
    response = requests.post(
        SPOTLIGHT_URL,
        data={'text': text, 'confidence': SPOTLIGHT_CONFIDENCE},
        headers={'Accept': 'application/json'})
    resources = response.json().get('Resources', [])
    matches = {}
    for resource in resources:
        dbpedia_uri = resource['@URI']
        similarity_score = float(resource['@similarityScore'])
        if similarity_score < SIMILARITY_CUTOUT:
            continue
        score = 'score: {:.2g}'.format(similarity_score)

        # types = ", ".join(resource['@types'].lower().split(','))
        # if types == '':
        #     types = None

        wikipedia_link = wikipedia_url(dbpedia_uri)
        concept_label = label(dbpedia_uri, fallback=True)
        match = {'type': 'link',
                 'uri': dbpedia_uri,
                 'description': concept_label,
                 'web': wikipedia_link,
                 'show': dbpedia_uri,
                 'extra': None,
                 'subscript': score,
                 'original': article_id}
        matches[dbpedia_uri] = match
    return matches

'''
Created on 1 Oct 2014

@author: RinkeHoekstra
'''

import json
from flask import request
from flask.ext.login import login_required
import requests
from bs4 import BeautifulSoup

from linkitup import app
from linkitup.util.baseplugin import plugin
from linkitup.util.provenance import provenance


@app.route('/s4', methods=['POST'])
@login_required
@plugin(fields=[('tags', 'id', 'name'), ('categories', 'id', 'name')],
        link='link')
@provenance()
def link_to_s4(*args, **kwargs):

    article_id = kwargs['article']['id']

    app.logger.debug("Running Ontotext S4 plugin for article {}".format(
        article_id))

    labels = ", ".join([item['label'] for item in kwargs['inputs']
                        + [kwargs['article']]])

    # Get article description, the wrapper does not provide it yet
    article = request.get_json()
    soup = BeautifulSoup(article['description'])
    description = soup.get_text()

    # Query text consists of article title, description, tags, and categories
    text = u"{}\n\n{}".format(description, labels)
    API_KEY = "s4io0o6gv3df"
    SECRET = "n5ko8i0j4ilb2dv"

    ontotext_s4_url = "https://text.s4.ontotext.com/v1/sbt"

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Encoding': 'gzip'}

    data = {
        'document': text,
        'documentType': 'text/plain',
        'annotationSelectors': []}

    r = requests.post(
        ontotext_s4_url,
        data=json.dumps(data),
        headers=headers,
        auth=(API_KEY, SECRET))

    resources = r.json().get('entities', [])
    matches = {}
    for s4_name, resource in resources.items():
        try:
            s4_uri = resource[0]['inst']
            s4_types = [resource[0]['class']]
        except KeyError as e:
            app.logger.error("Key error '{}' in {}".format(
                e.message, resource))
        else:
            match = {
                'type': 'link',
                'uri': s4_uri,
                'web': s4_uri,
                'show': s4_name,
                'extra': s4_types,
                'original': article_id
            }
            matches[s4_uri] = match

    return matches

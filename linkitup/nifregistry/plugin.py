'''
Created on 26 Mar 2013

@author: hoekstra
'''

from flask.ext.login import login_required

import xml.etree.ElementTree as ET
import requests
import re

from linkitup import app

from linkitup.util.baseplugin import plugin
from linkitup.util.provenance import provenance

NIF_REGISTRY_URL = "http://nif-services.neuinfo.org/nif/services/registry/search?q="

## TODO: generate direct derivedfrom relations between tags/categories
## and results. This requires successive querying of the NIF endpoint.


@app.route('/nifregistry', methods=['POST'])
@login_required
@plugin(fields=[('tags', 'id', 'name'), ('categories', 'id', 'name')],
        link='mapping')
@provenance()
def link_to_nif_registry(*args, **kwargs):
    # Retrieve the article id from the wrapper
    article_id = kwargs['article']['id']
    app.logger.debug("Running NIF Registry plugin for article {}".format(article_id))
    
    # Rewrite the tags and categories of the article in a form understood
    # by the NIF Registry
    match_items = kwargs['inputs']
    query_string = "".join(["'{}'".format(match_items[0]['label'])]
                        + [" OR '{}'".format(item['label'])
                            for item in match_items[1:]])
    query_url = NIF_REGISTRY_URL + query_string
    app.logger.debug("Query URL: {}".format(query_url))
    response = requests.get(query_url)
    if not response.ok:
        app.logger.error("Server returned status code {} {}".format(
            response.status_code, response.content))
        return {}
    tree = ET.fromstring(response.text.encode('utf-8'))
    matches = {}
    for result in tree.iter('registryResult'):
        match_uri = result.attrib['url']
        web_uri = result.attrib['url']
        display_uri = result.attrib['shortName'] or result.attrib['name']
        id_base = re.sub('\s|\(|\)', '_', result.attrib['name'])
        description = result[0].text[:600]
        nifid = result.attrib['id']
        entry_type = result.attrib['type']

        # Create the match dictionary
        match = {'type': "link",
                 'uri': match_uri,
                 'web': web_uri,
                 'show': display_uri,
                 'short': id_base,
                 'description': description,
                 'extra': nifid,
                 'subscript': entry_type,
                 'original': article_id}
        
        # Append it to all matches
        matches[match_uri] = match

    # Return the matches
    return matches

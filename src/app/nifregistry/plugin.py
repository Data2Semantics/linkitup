'''
Created on 26 Mar 2013

@author: hoekstra
'''

from flask import render_template, session, g
from flask.ext.login import login_required

import xml.etree.ElementTree as ET
import requests
import re

from app import app


NIF_REGISTRY_URL = "http://nif-services.neuinfo.org/nif/services/registry/search?q="


@app.route('/nifregistry/<article_id>')
@login_required
def link_to_nif_registry(article_id):
    app.logger.debug("Running NIF Registry plugin for article {}".format(article_id))
    
    # Retrieve the article from the session
    article = session['items'][article_id]
    
    # Rewrite the tags and categories of the article in a form understood by the NIF Registry
    match_items = article['tags'] + article['categories']
    
    query_string = "".join([ "'{}'".format(match_items[0]['name']) ] + [ " OR '{}'".format(item['name']) for item in match_items[1:]])
    
    
    query_url = NIF_REGISTRY_URL + query_string
    app.logger.debug("Query URL: {}".format(query_url))
    
    
    response = requests.get(query_url)
    
    tree = ET.fromstring(response.text.encode('utf-8'))
    
    matches = []
    
    for result in tree.iter('registryResult') :
        
        match_uri = result.attrib['url']
        web_uri = result.attrib['url']
        display_uri = result.attrib['shortName']
        
        if display_uri == "" or display_uri == None :
            display_uri = result.attrib['name']
            
        id_base = re.sub('\s|\(|\)','_',result.attrib['name'])
        description = result[0].text[:600]
        nifid = result.attrib['id']
        entry_type = result.attrib['type']
        original_qname = "FS{}".format(article_id)
        
        # Create the match dictionary
        match = {'type':    "link",
                 'uri':     match_uri,
                 'web':     web_uri,
                 'show':    display_uri,
                 'short':   id_base,
                 'description': description, 
                 'extra':   nifid,
                 'subscript': entry_type,
                 'original':original_qname}
        
        # Append it to all matches
        matches.append(match)
        

    # Add the matches to the session
    session.setdefault(article_id,[]).extend(matches)
    session.modified = True

    if matches == [] :
        matches = None
    
    # Return the matches
    return render_template('urls.html',
                           article_id = article_id, 
                           results = [{'title':'NIF Registry','urls': matches}])
    
        
        
    
    
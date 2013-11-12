'''
Created on 26 Mar 2013

@author: hoekstra
'''

from flask import render_template, g, request, jsonify
from flask.ext.login import login_required

import requests

from app import app

from app.util.baseplugin import plugin
from app.util.provenance import provenance

LLD_AUTOCOMPLETE_URL = "http://linkedlifedata.com/autocomplete.json"


@app.route('/linkedlifedata', methods=['POST'])
@login_required
@plugin(fields=[('tags','id','name'),('categories','id','name')], link='mapping')
@provenance()
def link_to_lld(*args, **kwargs):
    # Retrieve the article from the wrapper
    article_id = kwargs['article']['id']
    
    app.logger.debug("Running LinkedLifeData.com plugin for article {}".format(article_id))
    
    match_items = kwargs['inputs']
    
    search_parameters = {'limit': '2'}    

    matches = {}

    for item in match_items :
        
        search_parameters['q'] = item['label']
        original_id = item['id']
        
        response = requests.get(LLD_AUTOCOMPLETE_URL, params=search_parameters)
        
        hits = response.json()['results']
        
        for h in hits:
            app.logger.debug(h)
            
            match_uri = h['uri']['namespace'] + h['uri']['localName']
            web_uri = match_uri
            display_uri = h['label']
                
            id_base = h['uri']['localName']
            
                
            if 'types' in h:
                if len(h['types']) > 0 :
                    types = ", ".join(h['types'])
                else :
                    types = None
            elif 'type' in h:
                types = h['type']
            else :
                types = None
                
            if 'definition' in h :
                if h['definition'] != None :
                    if h['definition'].strip() != "" :
                        description = h['definition']
                    else :
                        description = None
                else :
                    description = None
            else :
                description = None
                
            score = "Score: {}".format(h['score'])
            
        
            
            
            # Create the match dictionary
            match = {'type':    "mapping",
                     'uri':     match_uri,
                     'web':     web_uri,
                     'show':    display_uri,
                     'short':   id_base,
                     'description': description, 
                     'extra':   types,
                     'subscript': score,
                     'original':original_id}
            

            # Append it to all matches
            matches[match_uri] = match

    
    # Return the matches
    return matches

'''
Created on 26 Mar 2013

@author: hoekstra
'''

from flask import render_template, g, request, jsonify
from flask.ext.login import login_required

import requests

from app import app


LLD_AUTOCOMPLETE_URL = "http://linkedlifedata.com/autocomplete.json"


@app.route('/linkedlifedata', methods=['POST'])
@login_required
def link_to_lld():
    # Retrieve the article from the post
    article = request.get_json()
    article_id = article['article_id']
    
    app.logger.debug("Running LinkedLifeData.com plugin for article {}".format(article_id))
    
    # Group together all tags and categories
    match_items = article['tags'] + article['categories']
    
    search_parameters = {'limit': '2'}    

    matches = {}

    for item in match_items :
        
        search_parameters['q'] = item['name']
        original_qname = "figshare_{}".format(item['id'])
        
        response = requests.get(LLD_AUTOCOMPLETE_URL, params=search_parameters)
        
        hits = response.json()['results']
        
        for h in hits:
            app.logger.debug(h)
            
            match_uri = h['uri']['namespace'] + h['uri']['localName']
            web_uri = match_uri
            display_uri = h['label']
                
            id_base = h['uri']['localName']
            
#            if len(h['labels']) > 0 :
#                description = ", ".join(h['labels'])
#            else :
#                description = None
                
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
                     'original':original_qname}
            

            # Append it to all matches
            matches[match_uri] = match


    if matches == {} :
        matches = None
    
    # Return the matches
    return jsonify({'title':'Linked Life Data','urls': matches})

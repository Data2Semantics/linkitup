'''
Created on 26 Mar 2013

@author: hoekstra
'''

from flask import render_template, session, g
from flask.ext.login import login_required

import requests

from app import app


LLD_AUTOCOMPLETE_URL = "http://linkedlifedata.com/autocomplete.json"


@app.route('/linkedlifedata/<article_id>')
@login_required
def link_to_lld(article_id):
    app.logger.debug("Running LinkedLifeData.com plugin for article {}".format(article_id))
    
    # Retrieve the article from the session
    article = session['items'][article_id]
    
    # Group together all tags and categories
    match_items = article['tags'] + article['categories']
    
    search_parameters = {'limit': '2'}    

    matches = []

    for item in match_items :
        
        search_parameters['q'] = item['name']
        original_qname = "figshare_{}".format(item['id'])
        
        response = requests.get(LLD_AUTOCOMPLETE_URL, params=search_parameters)
        
        hits = response.json()['results']
        
        for h in hits:
            match_uri = h['uri']['namespace'] + h['uri']['localName']
            web_uri = match_uri
            display_uri = h['label']
                
            id_base = h['uri']['localName']
            
#            if len(h['labels']) > 0 :
#                description = ", ".join(h['labels'])
#            else :
#                description = None
                
            if len(h['types']) > 0 :
                types = ", ".join(h['types'])
            else :
                types = None
                
            if h['definition'].strip() != "" :
                description = h['definition']
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
            matches.append(match)

        

    # Add the matches to the session
    session.setdefault(article_id,[]).extend(matches)
    session.modified = True

    if matches == [] :
        matches = None
    
    # Return the matches
    return render_template('urls.html',
                           article_id = article_id, 
                           results = [{'title':'Linked Life Data','urls': matches}])
    
        
        
    
    
"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   26 March 2013

Copyright (c) 2012,2013 Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from flask import render_template, session, g
from flask.ext.login import login_required


from app import app
from app.util.baseplugin import SPARQLPlugin





@app.route('/neurolex/<article_id>')
@login_required
def link_to_neurolex(article_id):
    app.logger.debug("Running Neurolex plugin for article {}".format(article_id))
    
    # Retrieve the article from the session
    article = session['items'][article_id]
    
    # Rewrite the tags and categories of the article in a form understood by utils.baseplugin.SPARQLPlugin
    article_items = article['tags'] + article['categories']
    match_items = [{'id': item['id'], 'label': item['name']} for item in article_items]
    
    try :
        # Initialize the plugin
        plugin = SPARQLPlugin(endpoint = "http://rdf-stage.neuinfo.org/ds/query",
                          template = "neurolex.query")
        
        # Run the plugin, and retrieve matches using the default label property (rdfs:label)
        matches = plugin.match(match_items)
        # Run the plugin with a NeuroLex specific property (namespace is defined in the neurolex.query template)
        matches.extend(plugin.match(match_items, property="property:Label"))
        
        # Add the matches to the session
        session.setdefault(article_id,[]).extend(matches)
        session.modified = True
    
        if matches == [] :
            matches = None
        
        # Return the matches
        return render_template('urls.html',
                               article_id = article_id, 
                               results = [{'title':'NeuroLex','urls': matches}])
        
    except Exception as e:
        return render_template( 'message.html',
                                type = 'error', 
                                text = e.message )


            


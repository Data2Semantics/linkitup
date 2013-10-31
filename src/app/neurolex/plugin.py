"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   26 March 2013

Copyright (c) 2012,2013 Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from flask import render_template, g, request, jsonify
from flask.ext.login import login_required


from app import app
from app.util.baseplugin import SPARQLPlugin





@app.route('/neurolex', methods=['POST'])
@login_required
def link_to_neurolex():
    # Retrieve the article from the post
    article = request.get_json()
    article_id = article['article_id']
    
    app.logger.debug("Running Neurolex plugin for article {}".format(article_id))
    
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
    
        if matches == [] :
            matches = None
        
        # Return the matches
        return jsonify({'title':'NeuroLex','urls': matches})
        
    except Exception as e:
        return render_template( 'message.html',
                                type = 'error', 
                                text = e.message )


            


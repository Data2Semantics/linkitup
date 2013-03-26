"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   2 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from flask import render_template, session, g
from flask.ext.login import login_required


from app import app
from app.util.baseplugin import SPARQLPlugin




@app.route('/dblp/<article_id>')
@login_required
def link_to_dblp(article_id):
    app.logger.debug("Running DBLP plugin for article {}".format(article_id))
    
    # Retrieve the article from the session
    article = session['items'][article_id]
    
    # Rewrite the authors of the article in a form understood by utils.baseplugin.SPARQLPlugin
    article_items = article['authors']
    match_items = [{'id': item['id'], 'label': item['full_name'].strip()} for item in article_items]
    
    try :
        # Initialize the plugin
        plugin = SPARQLPlugin(endpoint = "http://dblp.l3s.de/d2r/sparql",
                          template = "dblp.query")
        
        # Run the plugin, and retrieve matches using the FOAF name property
        matches = plugin.match_separately(match_items, property="foaf:name")
        
        # Add the matches to the session
        session.setdefault(article_id,[]).extend(matches)
        session.modified = True
    
        if matches == [] :
            matches = None
        
        # Return the matches
        return render_template('urls.html',
                               article_id = article_id, 
                               results = [{'title':'DBLP','urls': matches}])
        
    except Exception as e:
        return render_template( 'message.html',
                                type = 'error', 
                                text = e.message )

    


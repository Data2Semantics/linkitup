"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   2 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from flask.ext.login import login_required


from linkitup import app
from linkitup.util.baseplugin import plugin, SPARQLPlugin
from linkitup.util.provenance import provenance


@app.route('/dblp', methods=['POST'])
@login_required
@plugin(fields=[('authors','id','full_name')], link='mapping')
@provenance()
def link_to_dblp(*args, **kwargs):
        
    # Retrieve the article from the wrapper
    article_id = kwargs['article']['id']
    article_title = kwargs['article']['label']
    match_items = kwargs['inputs']
    
    app.logger.debug("Running DBLP plugin for article '{}' ({})".format(article_title, article_id))
    
    # Rewrite the authors of the article in a form understood by utils.baseplugin.SPARQLPlugin
    # article_items = article['authors']
    # match_items = [{'id': item['id'], 'label': item['full_name'].strip()} for item in article_items]
    
    try :
        # Initialize the plugin
        plugin = SPARQLPlugin(endpoint = "http://dblp.l3s.de/d2r/sparql",
                          template = "dblp.query")
        
        # Run the plugin, and retrieve matches using the FOAF name property
        matches = plugin.match_separately(match_items, property="foaf:name")
        
        # Return the matches
        return matches
        
    except Exception as e:
        return {'error': e.message}

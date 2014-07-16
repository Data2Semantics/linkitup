"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   2 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from flask.ext.login import login_required

import re

from app import app
from app.util.baseplugin import plugin, SPARQLPlugin
from app.util.provenance import provenance

endpoints = ['http://dbpedia-live.openlinksw.com/sparql', 'http://live.dbpedia.org/sparql', 'http://dbpedia.org/sparql']

@app.route('/dbpedia', methods=['POST'])
@login_required
@plugin(fields=[('tags','id','name'),('links','id','link')], link='mapping')
@provenance()
def link_to_wikipedia(*args,**kwargs):
    # Retrieve the article from the post
    article_id = kwargs['article']['id']
    match_items = kwargs['inputs']
    match_type = kwargs['link']

    app.logger.debug("Running DBPedia plugin for article {}".format(article_id))
    

    # Rewrite the match_items to strip the inchikey= prefix from the tag, if present. This allows the SPARQLPlugin to find additional matches for the dbpprop:inchikey property.
    match_items = [{'id': item['id'], 
                    'label': re.findall('^.*?\=(.*)$',item['label'])[0] if item['label'].lower().startswith('inchikey=') else item['label']} 
                    for item in match_items]
    
    try :
        # Initialize the plugin
        plugin = SPARQLPlugin(endpoint = endpoints,
                          template = "dbpedia.query",
                          match_type = match_type,
                          rewrite_function = lambda x: re.sub('dbpedia.org/resource','en.wikipedia.org/wiki',x),
                          id_function = lambda x: re.sub('http://dbpedia.org/resource/','',x),
                          id_base = 'uri')
        
        # Run the plugin, and retrieve matches using the default label property (rdfs:label)
        
        matches = plugin.match(match_items)
        # Run the plugin with a specific property for the InchiKeys (namespace is defined in the dbpedia.query template)
        matches.update(plugin.match(match_items, property="dbpprop:inchikey"))
        
        app.logger.debug("Plugin is done, returning the following matches")
        app.logger.debug(matches)
        
        # Return the matches
        return matches
        
    except Exception as e:
        app.logger.error(e.message)
        return {'error': e.message }
    


"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   2 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from flask.ext.login import login_required

import re

from linkitup import app
from linkitup.util.baseplugin import plugin, SPARQLPlugin
from linkitup.util.provenance import provenance

endpoints = ['http://marat.d2s.labs.vu.nl/sparql', 'http://dbpedia-live.openlinksw.com/sparql', 'http://live.dbpedia.org/sparql', 'http://dbpedia.org/sparql']

@app.route('/dbpedia', methods=['POST'])
@login_required
@plugin(fields=[('tags','id','name')], link='mapping')
@provenance()
def link_to_wikipedia(*args,**kwargs):
    # Retrieve the article from the post
    article_id = kwargs['article']['id']
    match_items = kwargs['inputs']
    match_type = kwargs['link']

    app.logger.debug("Running DBPedia plugin for article {}".format(article_id))

    # Rewrite the match_items to strip the inchikey= prefix from the tag, if present. This allows the SPARQLPlugin to find additional matches for the dbpprop:inchikey property.
    match_inchi = []
    match_rest = []
    for item in match_items:
        label = item['label']
        # InChiKeys are treated separately
        if label.lower().startswith('inchikey='):
            match_inchi.append({'id': item['id'], 'label': label.split('=')[0]})
        # Do not include tags which are already hyperlinks
        elif not label.startswith('http://'):
            match_rest.append({'id': item['id'], 'label': label})

    try:
        # Initialize the plugin
        plugin = SPARQLPlugin(
            endpoint=endpoints,
            template="dbpedia.query",
            match_type=match_type,
            rewrite_function=lambda x: re.sub('dbpedia.org/resource', 'en.wikipedia.org/wiki', x),
            id_function=lambda x: re.sub('http://dbpedia.org/resource/', '', x),
            id_base='uri')
        
        # Run the plugin, and retrieve matches using the default label property (rdfs:label)
        matches = plugin.match(match_rest)

        # FIXME Not tested, disabled until 5.10.14
        # Run the plugin with a specific property for the InchiKeys (namespace is defined in the dbpedia.query template)
        # plugin.template = "dbpedia_inchi.query"
        # matches.update(plugin.match(match_inchi, property="dbpprop:inchikey"))
        
        app.logger.debug("Plugin is done, returning the following matches")
        app.logger.debug(matches)
        
        # Return the matches
        return matches
        
    except Exception as e:
        app.logger.error(e.message)
        return {'error': e.message }
    


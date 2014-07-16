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

app.logger.debug("Initializing DrugBank")

endpoints = ['http://drugbank.bio2rdf.org/sparql','http://bioportal.bio2rdf.org/sparql','http://kegg.bio2rdf.org/sparql','http://affymetrix.bio2rdf.org/sparql']

@app.route('/bio2rdf', methods=['POST'])
@login_required
@plugin(fields=[('tags','id','name'),('categories','id','name')], link='mapping')
@provenance()
def link_to_bio2rdf(*args,**kwargs):
    # Retrieve the article from the post
    article_id = kwargs['article']['id']
    match_items = kwargs['inputs']
    match_type = kwargs['link']

    app.logger.debug("Running Bio2RDF plugin for article {}".format(article_id))
    

    try :
        # Initialize the plugin
        plugin = SPARQLPlugin(endpoint = endpoints,
                          template = "bio2rdf.query",
                          match_type = match_type,
                          id_base = 'label',
                          all=True)
        
        # Run the plugin, and retrieve matches using the default label property (rdfs:label)
        
        matches = plugin.match(match_items)
        
        app.logger.debug("Plugin is done, returning the following matches")
        app.logger.debug(matches)
        
        # Return the matches
        return matches
        
    except Exception as e:
        app.logger.error(e.message)
        return {'error': e.message }
    


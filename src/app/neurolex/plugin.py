"""

Module:	   plugin.py
Author:	   Rinke Hoekstra
Created:   26 March 2013

Copyright (c) 2012,2013 Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from flask.ext.login import login_required


from app import app
from app.util.baseplugin import plugin, SPARQLPlugin
from app.util.provenance import provenance




@app.route('/neurolex', methods=['POST'])
@login_required
@plugin(fields=[('tags','id','name'),('categories','id','name')], link='mapping')
@provenance()
def link_to_neurolex(*args, **kwargs):
	# Retrieve the article from the wrapper
	article_id = kwargs['article']['id']
	
	app.logger.debug("Running Neurolex plugin for article {}".format(article_id))
	
	match_items = kwargs['inputs']
	
	try :
		# Initialize the plugin
		plugin = SPARQLPlugin(endpoint = "http://rdf-stage.neuinfo.org/ds/query",
						  template = "neurolex.query")
		
		# Run the plugin, and retrieve matches using the default label property (rdfs:label)
		matches = plugin.match(match_items)

		app.logger.debug(matches)
		
		# Run the plugin with a NeuroLex specific property (namespace is defined in the neurolex.query template)
		specific_matches = plugin.match(match_items, property="property:Label")
		
		matches_keys_lower = {k.lower(): k for k,v in matches.items()}
		specific_keys_lower = {k.lower(): k for k,v in specific_matches.items()}
		
		app.logger.debug("Removing duplicates from matches")
		app.logger.debug(matches_keys_lower.keys())
		app.logger.debug(specific_keys_lower.keys())
		for k, K in specific_keys_lower.items():
			app.logger.debug(k)
			if not k in matches_keys_lower.items():
				app.logger.debug("{} is not in {}".format(k,matches_keys_lower))
				matches[K] = specific_matches[K]
		
		matches_keys_lower = {k.lower(): k for k,v in matches.items()}
		unique_matches = {}		
		for k, K in matches_keys_lower.items():
			unique_matches[K] = matches[K]

		app.logger.debug(unique_matches)
		
		# Return the matches
		return unique_matches
		
	except Exception as e:
		return {'error': e.message }


			


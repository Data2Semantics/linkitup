"""

Module:	   plugin.py
Author:	   Rinke Hoekstra
Created:   2 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from flask import render_template, g, request, jsonify
from flask.ext.login import login_required


from app import app
from app.util.baseplugin import SPARQLPlugin
from app.util.provenance import register




@app.route('/dblp', methods=['POST'])
@login_required
def link_to_dblp():
	prov = register('dblp')
		
	# Retrieve the article from the post
	article = request.get_json()
	article_id = article['article_id']
	article_title = article['title']
	
	prov.add(article_id, article_title)
	
	app.logger.debug("Running DBLP plugin for article '{}' ({})".format(article_title, article_id))
	
	# Rewrite the authors of the article in a form understood by utils.baseplugin.SPARQLPlugin
	article_items = article['authors']
	match_items = [{'id': item['id'], 'label': item['full_name'].strip()} for item in article_items]
	
	try :
		# Initialize the plugin
		plugin = SPARQLPlugin(endpoint = "http://dblp.l3s.de/d2r/sparql",
						  template = "dblp.query")
		
		# Run the plugin, and retrieve matches using the FOAF name property
		matches = plugin.match_separately(match_items, property="foaf:name")
		
	
		if matches == [] :
			matches = None
		
		# Return the matches
		return jsonify({'title':'DBLP','urls': matches})
		
	except Exception as e:
		return render_template( 'message.html',
								type = 'error', 
								text = e.message )

	


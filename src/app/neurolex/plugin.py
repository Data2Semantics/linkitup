"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   26 March 2013

Copyright (c) 2012,2013 Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from flask import render_template, session, g
from SPARQLWrapper import SPARQLWrapper, JSON
import re

from app import app

from flask.ext.login import login_required



@app.route('/neurolex/<article_id>')
@login_required
def link_to_neurolex(article_id):
    app.logger.debug("Running Neurolex plugin for article {}".format(article_id))
    
    items = session['items']

    sparql = SPARQLWrapper("http://rdf-stage.neuinfo.org/ds/query")
    sparql.setReturnFormat(JSON)
    
    urls = []

    i = items[article_id]
    
    tags_and_categories = i['tags'] + i['categories']
    
    if len(tags_and_categories) > 0 :
        
        for tag in tags_and_categories :
            t_id = tag['id']
            t_label = tag['name'].strip()
            t_qname = 'FS{}'.format(t_id)
            
            q = render_template("neurolex/neurolex.query", 
                                tag = t_label )
            
            sparql.setQuery(q)
    
            app.logger.debug(q)
            try :
                results = sparql.query().convert()
    
                for result in results["results"]["bindings"]:
                    match_uri = result["s"]["value"]
                    
                    short = re.sub('\s','_',t_label)
                    
                    if len(match_uri) > 61 :
                        show = match_uri[:29] + "..." + match_uri[-29:]
                    else :
                        show = match_uri
                    urls.append({'type': 'mapping', 'uri': match_uri, 'web': match_uri, 'show': show, 'short': short, 'original': t_qname})
            except :
                return render_template('message.html',
                                       type = 'error', 
                                       text = "NeuroLex endpoint {} produced unintelligible results. Maybe it's down?".format(sparql)
                                       )
        
            
    session.setdefault(article_id,[]).extend(urls)
    
    
    
    session.modified = True
    
    if urls == [] :
        urls = None
        
    
        
    return render_template('urls.html',
                           article_id = article_id, 
                           results = [{'title':'NeuroLex','urls': urls}])

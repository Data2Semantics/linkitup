"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   2 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from flask import render_template, session, g
from SPARQLWrapper import SPARQLWrapper, JSON
import re

from app import app

from flask.ext.login import login_required



@app.route('/dblp/<article_id>')
@login_required
def link_to_dblp(article_id):
    app.logger.debug("Running DBLP plugin for article {}".format(article_id))
    
    items = session['items']

    sparql = SPARQLWrapper("http://dblp.l3s.de/d2r/sparql")
    sparql.setReturnFormat(JSON)
    
    authors = []

    i = items[article_id]
    
    if len(i['authors']) > 0 :
        
        for author in i['authors'] :
            a_id = author['id']
            a_label = author['full_name'].strip()
            a_qname = 'FS{}'.format(a_id)
            
            q = """
                PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                
                SELECT ?s 
                WHERE {
                    ?s a foaf:Agent .
                    ?s foaf:name '"""+a_label+"""'.
                }
            """
            
            sparql.setQuery(q)
    
            app.logger.debug(q)
            try :
                results = sparql.query().convert()
    
                for result in results["results"]["bindings"]:
                    match_uri = result["s"]["value"]
                    
                    short = re.sub('\s','_',a_label)
                    
                    if len(match_uri) > 61 :
                        show = match_uri[:29] + "..." + match_uri[-29:]
                    else :
                        show = match_uri
                    authors.append({'type': 'mapping', 'uri': match_uri, 'web': match_uri, 'show': show, 'short': short, 'original': a_qname})
            except :
                return render_template('message.html',
                                       type = 'error', 
                                       text = "DBLP endpoint {} produced unintelligible results. Maybe it's down?".format(sparql)
                                       )
        
            
    session.setdefault(article_id,[]).extend(authors)
    
    
    
    session.modified = True
    
    if authors == [] :
        authors = None
        
    
        
    return render_template('urls.html',
                           article_id = article_id, 
                           results = [{'title':'DBLP','urls': authors}])

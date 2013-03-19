"""

Module:    plugin.py
Author:    Rinke Hoekstra
Created:   2 October 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from SPARQLWrapper import SPARQLWrapper, JSON
from django.shortcuts import render_to_response
import re





def linkup(request, article_id):
    items = request.session['items']

    sparql = SPARQLWrapper("http://dblp.l3s.de/d2r/sparql")
    sparql.setReturnFormat(JSON)
    
    authors = []

    i = items[article_id]
    
    if len(i['authors']) > 0 :
        
        first_author = i['authors'][1]
        a_id = first_author['id']
        a_label = first_author['full_name'].strip()
        a_qname = 'FS{}'.format(a_id)
        
        q_part = "{ ?s a foaf:Agent .\n\t\t ?s foaf:name '"+a_label+"'. } "
        
        for author in i['authors'][2:] :
            a_id = author['id']
            a_label = author['full_name'].strip()
            a_qname = 'FS{}'.format(a_id)
            
            q_part += "\n\t\tUNION { ?s a foaf:Agent .\n\t\t ?s foaf:name '"+a_label+"'. } "
            
        q = """
            PREFIX foaf: <http://xmlns.com/foaf/0.1/>
            
            SELECT ?s 
            WHERE {
                """ + q_part + """
            }
        """
        
        sparql.setQuery(q)
        
        print "Set query to "+q
    
        try :
            print "Calling endpoint"
            results = sparql.query().convert()
            print "Done"
            
            for result in results["results"]["bindings"]:
                match_uri = result["s"]["value"]
                
                print match_uri
                
                short = re.sub('\s','_',a_label)
                
                if len(match_uri) > 61 :
                    show = match_uri[:29] + "..." + match_uri[-29:]
                else :
                    show = match_uri
                authors.append({'type': 'mapping', 'uri': match_uri, 'web': match_uri, 'show': show, 'short': short, 'original': a_qname})
        except :
            return render_to_response('message.html',{'type': 'error', 'text':"DBLP endpoint {} produced unintelligible results. Maybe it's down?".format(sparql)})
    
            
    request.session.setdefault(article_id,[]).extend(authors)
    request.session.modified = True
    
    if authors == [] :
        authors = None
        
    
        
    return render_to_response('urls.html',{'article_id': article_id, 'results':[{'title':'DBLP','urls': authors}]})

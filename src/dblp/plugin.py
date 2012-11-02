'''
Created on 2 Oct 2012

@author: hoekstra
'''
from SPARQLWrapper import SPARQLWrapper, JSON
from django.shortcuts import render_to_response
import re





def linkup(request, article_id):
    items = request.session['items']

    sparql = SPARQLWrapper("http://dblp.l3s.de/d2r/sparql")
    sparql.setReturnFormat(JSON)
    
    authors = []

    for i in items :
        if str(i['article_id']) == str(article_id):
            
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
                        return render_to_response('message.html',{'type': 'error', 'text':"DBLP endpoint {} produced unintelligible results. Maybe it's down?".format(sparql)})
            
            
    request.session.setdefault(article_id,[]).extend(authors)
    request.session.modified = True
    
    if authors == [] :
        authors = None
        
    
        
    return render_to_response('urls.html',{'article_id': article_id, 'results':[{'title':'DBLP','urls': authors}]})

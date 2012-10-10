'''
Created on 2 Oct 2012

@author: hoekstra
'''
from SPARQLWrapper import SPARQLWrapper, JSON
from django.shortcuts import render_to_response
import re





def linkup(request, article_id):
    items = request.session['items']

    sparql = SPARQLWrapper("http://www4.wiwiss.fu-berlin.de/dblp/sparql")
    sparql.setReturnFormat(JSON)
    
    authors = []

    for i in items :
        # print i['article_id'], article_id
        if str(i['article_id']) == str(article_id):
            # print "{} is the id we were looking for".format(article_id)
            
            if len(i['authors']) > 0 :
                # print "Checking for authors..."
                
                for author in i['authors'] :
                    a_id = author['id']
                    # print a_id
                    a_label = author['full_name'].strip()
                    # print a_label
                    a_qname = 'FS{}'.format(a_id)
                    # print a_qname
                    
                    q = """
                        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
                        
                        SELECT ?s 
                        WHERE {
                            ?s a foaf:Person .
                            ?s foaf:name '"""+a_label+"""'.
                        }
                    """
                    
                    # print q
                    
                    sparql.setQuery(q)
                    
                    # print "query ran"
    
                    try :
                        results = sparql.query().convert()
    
                        # print "DBLP done"
                        for result in results["results"]["bindings"]:
                            match_uri = result["s"]["value"]
                            # print match_uri
                            
                            short = re.sub('\s','_',a_label)
                            
                            if len(match_uri) > 61 :
                                show = match_uri[:29] + "..." + match_uri[-29:]
                            else :
                                show = match_uri
                            authors.append({'uri': match_uri, 'web': match_uri, 'show': show, 'short': short, 'original': a_qname})
                    except :
                        return render_to_response('message.html',{'type': 'error', 'text':"DBLP endpoint {} produced unintelligible results. Maybe it's down?".format(sparql)})
            
            
    request.session[article_id] = authors
    
    if authors == [] :
        authors = None
        
    
        
    return render_to_response('urls.html',{'article_id': article_id, 'results':[{'title':'DBLP','urls': authors}]})

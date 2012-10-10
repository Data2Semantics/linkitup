'''
Created on Sep 21, 2012

@author: hoekstra
'''

from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, render
from django.template import RequestContext
import requests
from oauth_hook import OAuthHook
from urlparse import parse_qs
import json
from models import User
from SPARQLWrapper import SPARQLWrapper, JSON
from rdflib import ConjunctiveGraph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, SKOS, OWL
import re
import urllib
from datetime import datetime



OAuthHook.consumer_key = 'K9qG70PgROIg8CpZGJlGRg'
OAuthHook.consumer_secret = '0JdZcz5pz0HwyWbeiwsviA'
token_key = 'tGEwr1GEEUEZ0nSO4rMBNAM4FDgldcpxsIlbyYX5GN5AtGEwr1GEEUEZ0nSO4rMBNA'
token_secret = 'AHQVsrioP9AqJ8dUoQvx9A'


def index(request):
    if request.session.get('oauth_token',None) == None :
        # print "First"
        figshare_oauth_hook = OAuthHook(header_auth=True)
        response = requests.post('http://api.figshare.com/v1/pbl/oauth/request_token', hooks={'pre_request': figshare_oauth_hook})
        # print response.text
        qs = parse_qs(response.text)
        oauth_request_token = qs['oauth_token'][0]
        oauth_request_token_secret = qs['oauth_token_secret'][0]
    
        request.session['oauth_request_token'] = oauth_request_token
        request.session['oauth_request_token_secret'] = oauth_request_token_secret
    
        # print "Second"
        authorize_url = "https://api.figshare.com/v1/pbl/oauth/authorize?oauth_token={}".format(oauth_request_token)
        # print "Redirecting to {} allow the app".format(authorize_url)
    
        return render_to_response('allow_application.html',{'authorize_url': authorize_url},context_instance=RequestContext(request))
#    elif request.session.get('oauth_token',None) == None :
#        return render_to_response('enter_pin.html',context_instance=RequestContext(request))
    else :
        oauth_token = request.session.get('oauth_token')
        oauth_token_secret = request.session.get('oauth_token_secret')
        xoauth_figshare_id = request.session.get('xoauth_figshare_id')
        
        oauth_hook = OAuthHook(oauth_token, oauth_token_secret, header_auth=True)

        client = requests.session(hooks={'pre_request': oauth_hook})

        response = client.get('http://api.figshare.com/v1/my_data/articles')
        results = json.loads(response.content)
        
        request.session['items'] = results['items']
        
        # print results
        
        return render_to_response('articles.html',{'raw': str(results),'results': results},context_instance=RequestContext(request))
        
        
def linkup(request, article_id):
    # print article_id
    items = request.session['items']
    # print items
    
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    sparql.setReturnFormat(JSON)
    
    dblp = SPARQLWrapper("http://www4.wiwiss.fu-berlin.de/dblp/sparql")
    dblp.setReturnFormat(JSON)
    

    
    urls = []
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
                    
                    dblp.setQuery(q)
                    
                    # print "query ran"
    
                    try :
                        results = dblp.query().convert()
    
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
                        print "DBLP endpoint {} produced unintelligible results. Maybe it's down?".format(dblp)
            
            
            tags_and_categories = i['tags'] + i['categories']
            for tag in tags_and_categories :
                # print tag
                
                t_id = tag['id']
                t_label = tag['name'].strip()
                t_qname = 'FS{}'.format(t_id)

                if t_label.lower().startswith('inchikey=') :
                    t_match = re.findall('^.*?\=(.*)$',t_label)[0]
                    # print t_match
                    
                    q = """
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        PREFIX dbpprop: <http://dbpedia.org/property/> 
                        SELECT ?s
                        WHERE { 
                            ?s dbpprop:inchikey ?label .
                            ?label bif:contains '\""""+t_match+"""\"' .
                            FILTER (regex(str(?label), '^"""+t_match+"""$', 'i')).
                            FILTER (regex(str(?s), '^http://dbpedia.org/resource')).
                        	FILTER (!regex(str(?s), '^http://dbpedia.org/resource/Category:')). 
                        	FILTER (!regex(str(?s), '^http://dbpedia.org/resource/List')).
                        	FILTER (!regex(str(?s), '^http://sw.opencyc.org/')). 
                        }
                    """
                else :
                    t_match = t_label
                    q = """
                        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
                        SELECT ?s
                        WHERE { 
                            ?s rdfs:label ?label .
                            ?label bif:contains '\""""+t_match+"""\"' .
                            FILTER (regex(str(?label), '^"""+t_match+"""$', 'i')).
                            FILTER (regex(str(?s), '^http://dbpedia.org/resource')).
                        	FILTER (!regex(str(?s), '^http://dbpedia.org/resource/Category:')). 
                        	FILTER (!regex(str(?s), '^http://dbpedia.org/resource/List')).
                        	FILTER (!regex(str(?s), '^http://sw.opencyc.org/')). 
                        }
                    """
                sparql.setQuery(q)

                results = sparql.query().convert()
                # print "DBpedia done"
                for result in results["results"]["bindings"]:
                    match_uri = result["s"]["value"]
                    # print match_uri
                    
                    wikipedia_uri = re.sub('dbpedia.org/resource','en.wikipedia.org/wiki',match_uri)
                    
                    short = re.sub('http://dbpedia.org/resource/','',match_uri)
                    # print wikipedia_uri
                    
                    if len(wikipedia_uri) > 61 :
                        show = wikipedia_uri[:29] + "..." + wikipedia_uri[-29:]
                    else :
                        show = wikipedia_uri
                    
                    urls.append({'uri': match_uri, 'web': wikipedia_uri, 'show': show, 'short': short, 'original': t_qname})
                    

    
    
    request.session[article_id] = urls + authors
    
    if urls == [] :
        urls = None 
    if authors == [] :
        authors = None
        
    
        
    return render_to_response('urls.html',{'article_id': article_id, 'results':[{'title':'Wikipedia','urls': urls},{'title':'DBLP','urls': authors}]})


def process(request, article_id):
    if request.POST['task'] == "Download RDF" :
        return rdf(request,article_id)
    elif request.POST['task'] == "Add to Figshare":
        return update(request,article_id)
    else:
        return HttpResponse("No idea what you meant...")

def rdf(request, article_id):
    checked_urls = request.POST.getlist('url')
    
    FSV = Namespace('http://figshare.com/vocab/')
    FS = Namespace('http://figshare.com/resource/')
    DBPEDIA = Namespace('http://dbpedia.org/resource/')
    FOAF = Namespace('http://xmlns.com/foaf/0.1/')
    
    g = ConjunctiveGraph()
    g.bind('fsv',FSV)
    g.bind('fs',FS)
    g.bind('skos',SKOS)
    g.bind('dbpedia',DBPEDIA)
    g.bind('foaf',FOAF)
    
    items = request.session.get('items',[])
    
    urls = request.session.get(article_id,[])
        
    for i in items :
        # print i['article_id'], article_id
        if str(i['article_id']) == str(article_id):
            # print "{} is the id we were looking for".format(article_id)
            doi = i['doi']
            
            article_id_qname = 'FS{}'.format(article_id)
            
            g.add((URIRef(doi),FSV['article_id'],Literal(article_id)))
            g.add((URIRef(doi),OWL.sameAs,FS[article_id_qname]))
            
            # print "Processing owner..."
            owner = i['owner']
            o_id = owner['id']
            o_label = owner['full_name']
            o_qname = 'FS{}'.format(o_id)
                    
            g.add((URIRef(doi),FSV['owner'],FS[o_qname]))
            g.add((FS[o_qname],FOAF['name'],Literal(o_label)))
            g.add((FS[o_qname],FSV['id'],Literal(o_id)))
            g.add((FS[o_qname],RDF.type,FSV['Owner']))
            
            # print "Processing defined type"
            dt = i['defined_type']
            o_qname = 'FS{}'.format(urllib.quote(dt))
                    
            g.add((URIRef(doi),FSV['defined_type'],FS[o_qname]))
            g.add((FS[o_qname],SKOS.prefLabel,Literal(dt)))
            g.add((FS[o_qname],RDF.type,FSV['DefinedType']))
            
            # print "Processing published date"
            date = i['published_date']
            pydate = datetime.strptime(date,'%H:%M, %b %d, %Y')
            g.add((URIRef(doi),FSV['published_date'],Literal(pydate)))
            
            # print "Processing description"
            description = i['description']
            g.add((URIRef(doi),SKOS.description, Literal(description)))

            if len(i['authors']) > 0 :
                # print "Processing authors..."
                author_count = 0 
                seq = BNode()
                
                g.add((URIRef(doi),FSV['authors'],seq))
                g.add((seq,RDF.type,RDF.Seq))
                
                for author in i['authors'] :
                    a_id = author['id']
                    a_label = author['full_name']
                    a_first = author['first_name']
                    a_last = author['last_name']
                    a_qname = 'FS{}'.format(a_id)
                    
                    author_count = author_count + 1
                    
                    member = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#_{}'.format(author_count))
                    g.add((seq,member,FS[a_qname]))
                    g.add((FS[a_qname],FOAF['name'],Literal(a_label)))
                    g.add((FS[a_qname],FOAF['firstName'],Literal(a_first)))
                    g.add((FS[a_qname],FOAF['lastName'],Literal(a_last)))
                    g.add((FS[a_qname],FSV['id'],Literal(a_id)))
                    g.add((FS[a_qname],RDF.type,FSV['Author']))
            

            
            # print "Processing tags..."
            for tag in i['tags'] :
                # print tag
                
                t_id = tag['id']
                t_label = tag['name']
                t_qname = 'FS{}'.format(t_id)

                g.add((URIRef(doi),FSV['tag'],FS[t_qname]))
                g.add((FS[t_qname],SKOS.prefLabel,Literal(t_label)))
                g.add((FS[t_qname],FSV['id'],Literal(t_id)))   
                g.add((FS[t_qname],RDF.type,FSV['Tag']))
                
            # print "Processing links..."
            for link in i['links'] :
                # print link
                l_id = link['id']
                l_value = link['link']
                l_qname = 'FS{}'.format(l_id)
                
                g.add((URIRef(doi),FSV['link'],FS[l_qname]))
                g.add((FS[l_qname],FSV['id'],Literal(l_id)))
                g.add((FS[l_qname],RDFS.seeAlso,URIRef(l_value))) 
                g.add((FS[l_qname],FOAF['page'],URIRef(l_value))) 
                g.add((FS[l_qname],RDF.type,FSV['Link']))
                
                # print "Checking if link matches a Wikipedia/DBPedia page..."
                
                if l_value.startswith('http://en.wikipedia.org/wiki/') :
                    l_match = re.sub('http://en.wikipedia.org/wiki/','http://dbpedia.org/resource/',l_value)
                    g.add((FS[l_qname],SKOS.exactMatch,URIRef(l_match)))
                
            # print "Processing files..."
            for file in i['files'] :
                # print file
                f_id = file['id']
                f_value = file['name']
                f_mime = file['mime_type']
                f_size = file['size']
                f_qname = 'FS{}'.format(f_id)
                
                g.add((URIRef(doi),FSV['file'],FS[f_qname]))
                g.add((FS[f_qname],FSV['id'],Literal(f_id)))
                g.add((FS[f_qname],RDFS.label,Literal(f_value))) 
                g.add((FS[f_qname],FSV['mime_type'],Literal(f_mime)))
                g.add((FS[f_qname],FSV['size'],Literal(f_size)))
                g.add((FS[f_qname],RDF.type,FSV['File']))
                
            # print "Processing categories..."
            for cat in i['categories'] :
                # print cat
                c_id = cat['id']
                c_value = cat['name']
                c_qname = 'FS{}'.format(c_id)
                
                g.add((URIRef(doi),FSV['category'],FS[c_qname]))
                g.add((FS[c_qname],FSV['id'],Literal(c_id)))
                g.add((FS[c_qname],RDFS.label,Literal(c_value))) 
                g.add((FS[c_qname],RDF.type,FSV['Category']))
    
    for u in urls :
        if u['uri'] in checked_urls :       
            original_qname = u['original']
            uri = u['uri']
                    
            g.add((FS[original_qname],SKOS.exactMatch,URIRef(uri) ))

             
                        
    graph = g.serialize(format='turtle')
    response = HttpResponse(graph, content_type = 'text/turtle')
    response['Content-Disposition'] = 'attachment; filename={}.ttl'.format(article_id)
    return response




def update(request, article_id):
    checked_urls = request.POST.getlist('url')
    
    
    oauth_token = request.session.get('oauth_token')
    oauth_token_secret = request.session.get('oauth_token_secret')
    xoauth_figshare_id = request.session.get('xoauth_figshare_id')
        
    oauth_hook = OAuthHook(oauth_token, oauth_token_secret, header_auth=True)

    client = requests.session(hooks={'pre_request': oauth_hook})
    
    urls = request.session.get(article_id,[])
    
    for u in urls :
        if u['uri'] in checked_urls :
            # print u['uri']
            body = {'link': u['web']}
            headers = {'content-type':'application/json'}
        
            response = client.put('http://api.figshare.com/v1/my_data/articles/{}/links'.format(article_id),
                                data=json.dumps(body), headers=headers)
            results = json.loads(response.content)
            # print results
    
    body = {'tag_name': 'Enriched with LinkItUp'}
    headers = {'content-type':'application/json'}
        
    response = client.put('http://api.figshare.com/v1/my_data/articles/{}/tags'.format(article_id),
                                data=json.dumps(body), headers=headers)
    results = json.loads(response.content)
    # print results
            
    return HttpResponseRedirect('/')


def pin(request):
    
    oauth_verifier = request.POST['pin']
    oauth_request_token = request.session.get('oauth_request_token')
    oauth_request_token_secret = request.session.get('oauth_request_token_secret')
    
    
    # print oauth_verifier, oauth_request_token, oauth_request_token_secret
    # print "Third"
    new_figshare_oauth_hook = OAuthHook(oauth_request_token, oauth_request_token_secret, header_auth=True)
    response = requests.post('http://api.figshare.com/v1/pbl/oauth/access_token', {'oauth_verifier': oauth_verifier}, hooks={'pre_request': new_figshare_oauth_hook})
    response = parse_qs(response.content)
    
    if response == {} :
        return HttpResponse('Authorization failed')
    else :
        # print response 
        oauth_token = response['oauth_token'][0]
        oauth_token_secret = response['oauth_token_secret'][0]
        xoauth_figshare_id = response['xoauth_figshare_id'][0]
    
        request.session['oauth_token'] = oauth_token
        request.session['oauth_token_secret'] = oauth_token_secret
        request.session['xoauth_figshare_id'] = xoauth_figshare_id
    
        return(HttpResponseRedirect('/'))

    

    
def clear(request):
    request.session.clear()
    
    return(HttpResponse('Session data cleared!'))
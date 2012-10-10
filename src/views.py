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
from rdflib import ConjunctiveGraph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, SKOS, OWL
import re
import urllib
from datetime import datetime
import yaml



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
#        xoauth_figshare_id = request.session.get('xoauth_figshare_id')
        
        oauth_hook = OAuthHook(oauth_token, oauth_token_secret, header_auth=True)

        client = requests.session(hooks={'pre_request': oauth_hook})

        response = client.get('http://api.figshare.com/v1/my_data/articles')
        results = json.loads(response.content)
        
        
        request.session['items'] = results['items']
        
        print "Loading plugins"
        plugins = yaml.load(open('plugins.yaml','r'))
#        print plugins
        
        map(__import__, plugins.keys())
        
#        print results
        
        return render_to_response('articles.html',{'raw': str(results),'results': results, 'plugins': plugins.values()},context_instance=RequestContext(request))
        
        


def process(request, article_id):
    if request.POST['task'] == "Download RDF" :
        print "Going to download RDF"
        return rdf(request,article_id)
    elif request.POST['task'] == "Add to Figshare":
        print "Adding to Figshare"
        return update(request,article_id)
    else:
        return HttpResponse("No idea what you meant...")



def getRDF(request, article_id):
    checked_urls = request.POST.getlist('url')
    
    FSV = Namespace('http://figshare.com/vocab/')
    FS = Namespace('http://figshare.com/resource/')
    DBPEDIA = Namespace('http://dbpedia.org/resource/')
    FOAF = Namespace('http://xmlns.com/foaf/0.1/')
    DCTERMS = Namespace('http://purl.org/dc/terms/')
    
    g = ConjunctiveGraph()
    g.bind('fsv',FSV)
    g.bind('fs',FS)
    g.bind('skos',SKOS)
    g.bind('dbpedia',DBPEDIA)
    g.bind('foaf',FOAF)
    g.bind('dcterms',DCTERMS)
    
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
            for f in i['files'] :
                # print f
                f_id = f['id']
                f_value = f['name']
                f_mime = f['mime_type']
                f_size = f['size']
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
    
    
    selected_urls = [u for u in urls if u['uri'] in checked_urls]
    
    
    for u in selected_urls :      
        original_qname = u['original']
        uri = u['uri']
                    
        if u['type'] == 'mapping':
            g.add((FS[original_qname],SKOS.exactMatch,URIRef(uri) ))
        elif u['type'] == 'reference':
            g.add((FS[original_qname],DCTERMS['references'],URIRef(uri) ))
        else :
            g.add((FS[original_qname],SKOS.related, URIRef(uri)))

    return g

def rdf(request, article_id):
    g = getRDF(request, article_id)

    graph = g.serialize(format='turtle')
    response = HttpResponse(graph, content_type = 'text/turtle')
    response['Content-Disposition'] = 'attachment; filename={}.ttl'.format(article_id)
    return response




def update(request, article_id):
    checked_urls = request.POST.getlist('url')
    
    
    oauth_token = request.session.get('oauth_token')
    oauth_token_secret = request.session.get('oauth_token_secret')
#    xoauth_figshare_id = request.session.get('xoauth_figshare_id')
        
    oauth_hook = OAuthHook(oauth_token, oauth_token_secret, header_auth=True)

    client = requests.session(hooks={'pre_request': oauth_hook})
    
    urls = request.session.get(article_id,[])
    
    print "Checked urls: ", checked_urls
    for u in urls :
#        print "Looking at {}".format(u['uri'])
        
        if u['uri'] in checked_urls :
            body = {'link': u['web']}
            headers = {'content-type':'application/json'}
        
            response = client.put('http://api.figshare.com/v1/my_data/articles/{}/links'.format(article_id),
                                data=json.dumps(body), headers=headers)
            results = json.loads(response.content)
            print "Added {} with the following results:\n".format(u['uri']), results
    
    body = {'tag_name': 'Enriched with LinkItUp'}
    headers = {'content-type':'application/json'}
        
    response = client.put('http://api.figshare.com/v1/my_data/articles/{}/tags'.format(article_id),
                                data=json.dumps(body), headers=headers)
    
    ## The below doesn't work as it replaces the files currently attached to the article!
#    g = getRDF(request, article_id)
#    graph = g.serialize(format='turtle')
#    
#    
#    files = {'filedata':('metadata.ttl', graph)}
#
#    response = client.put('http://api.figshare.com/v1/my_data/articles/{}/files'.format(article_id),
#                      files=files)
#    results = json.loads(response.content)
    # print results
            
    # Reset the URLs generated by the application
    request.session[article_id] = []
    request.session.modified = True
    
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

"""

Module:    rdf.py
Author:    Rinke Hoekstra
Created:   2 November 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from flask import session, g

from rdflib import Graph, ConjunctiveGraph, Namespace, URIRef, Literal, BNode, plugin
from rdflib.store import Store
from rdflib.namespace import RDF, RDFS, SKOS, OWL
from urllib import quote
from datetime import datetime
import re

from app import app

LUV = Namespace('http://linkitup.data2semantics.org/vocab/')
LU = Namespace('http://linkitup.data2semantics.org/resource/')
DBPEDIA = Namespace('http://dbpedia.org/resource/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
DCTERMS = Namespace('http://purl.org/dc/terms/')
NANOPUB = Namespace('http://www.nanopub.org/nschema#')
PROV = Namespace('http://www.w3.org/ns/prov#')
OA = Namespace('http://www.w3.org/ns/oa#')


def associate_namespaces(graph):
    graph.bind('luv',LUV)
    graph.bind('lu',LU)
    graph.bind('skos',SKOS)
    graph.bind('dbpedia',DBPEDIA)
    graph.bind('foaf',FOAF)
    graph.bind('dcterms',DCTERMS)
    graph.bind('nanopub',NANOPUB)
    graph.bind('prov',PROV)
    graph.bind('oa',OA)
    
    return graph



def get_trix(article_id, checked_urls):
    graph = get_rdf(article_id, checked_urls)

    graphFile = graph.serialize(format='trix')
    
    return graphFile
   
def get_trig(article_id, checked_urls): 
    graph = get_rdf(article_id, checked_urls)

    graphFile = graph.serialize(format='trix')
    
    return graphFile


def get_rdf(article_id, checked_urls):
    """Takes everything we know about the article specified in article_id, and builds a simple RDF graph. 
    
    We only consider the URLs of checkboxes that were selected by the user.
    
    Returns the RDF graph as a ConjunctiveGraph"""
    
    items = session.get('items',[])
    
    urls = session.get(article_id,[])
        
    i = items[article_id]

    article_id_qname = 'figshare_{}'.format(article_id)
    
    

    
    nano = LU["nanopublication/{}".format(article_id_qname)]
    assertion = LU["assertion/{}".format(article_id_qname)]
    provenance = LU["provenance/{}".format(article_id_qname)]
    # We don't provide any 'supporting' information for the nanopublication
    
    store = plugin.get('IOMemory', Store)()
    
    np_graph = Graph(store, identifier=nano)
    a_graph = Graph(store, identifier=assertion)
    p_graph = Graph(store, identifier=provenance)
    
    np_graph = associate_namespaces(np_graph)
    a_graph = associate_namespaces(a_graph)
    p_graph = associate_namespaces(p_graph)
    
    
    # A bit annoying, but we need both the DOI and the Owner before we can start
    
    if 'doi' in i:
        # If the article has a DOI assigned, we will use it in our RDF rendering
        doi = i['doi']
        
        article_uri = URIRef(doi)
        a_graph.add((article_uri,OWL.sameAs,LU[article_id_qname]))
        a_graph.add((article_uri,LUV['doi'],URIRef(doi)))
    else :
        # If it doesn't, we'll use a URI of our own making
        article_uri = LU[article_id_qname]    

    # print "Processing owner..."
    if 'owner' in i:
        owner = i['owner']
        o_id = owner['id']
        o_label = owner['full_name']
        o_qname = 'figshare_{}'.format(o_id)
        
        owner_uri = LU[o_qname]
                
        a_graph.add((article_uri,LUV['owner'],owner_uri))
        a_graph.add((LU[o_qname],FOAF['name'],Literal(o_label)))
        a_graph.add((LU[o_qname],LUV['id'],Literal(o_id)))
        a_graph.add((LU[o_qname],RDF.type,LUV['Owner']))
    else :
        owner_uri = None


    # Add the stuff necessary to define the nanopublication
    np_graph.add((nano, RDF.type, NANOPUB['Nanopublication']))
    np_graph.add((nano, NANOPUB['hasAssertion'], assertion))
    np_graph.add((nano, NANOPUB['hasProvenance'], provenance))
    



    now = datetime.now()
    nowstr = datetime.now().strftime("%Y-%m-%dT%H:%M:%S%z")

    # Add the necessary provenance information
    
    user_qname = re.sub(' ','_', g.user.nickname)
    user_uri = LU['person/{}'.format(user_qname)]
    
    activity_uri = LU['linkitup_{}'.format(nowstr)]
   
    p_graph.add((nano, RDF.type, PROV['Entity']))
    
    p_graph.add((nano, PROV['wasGeneratedBy'], activity_uri))
    p_graph.add((nano, PROV['wasGeneratedAt'], Literal(now)))
    p_graph.add((nano, PROV['wasAttributedTo'], user_uri))
    
    p_graph.add((activity_uri, PROV['used'], article_uri))
    p_graph.add((activity_uri, PROV['generated'], nano))
    p_graph.add((activity_uri, PROV['endedAtTime'], Literal(now)))
    p_graph.add((activity_uri, PROV['wasStartedBy'], user_uri))
    p_graph.add((activity_uri, PROV['wasInfluencedBy'], URIRef('http://linkitup.data2semantics.org')))    
 
    p_graph.add((user_uri, RDF.type, PROV['Person']))
    p_graph.add((user_uri, RDF.type, PROV['Agent']))
    p_graph.add((user_uri, RDF.type, FOAF['Person']))
    
    p_graph.add((user_uri, FOAF['name'], Literal(g.user.nickname)))
    
    p_graph.add((URIRef('http://linkitup.data2semantics.org'), RDF.type, PROV['SoftwareAgent']))
    p_graph.add((URIRef('http://linkitup.data2semantics.org'), RDF.type, PROV['Agent']))
    
    p_graph.add((URIRef('http://linkitup.data2semantics.org'), FOAF['name'], Literal('Linkitup')))

    p_graph.add((article_uri, RDF.type, PROV['Entity']))
    
    if owner_uri :
        p_graph.add((article_uri, PROV['wasAttributedTo'], owner_uri))

    # Add the stuff necessary to define the Open Annotation annotation
    p_graph.add((nano, RDF.type, OA['Annotation']))
    p_graph.add((nano, OA['hasBody'], assertion))
    p_graph.add((nano, OA['hasTarget'], article_uri))
    
    p_graph.add((nano, OA['wasAnnotatedBy'], user_uri))
    p_graph.add((nano, OA['wasAnnotatedAt'], Literal(now)))

    a_graph.add((article_uri,LUV['article_id'],Literal(article_id)))

    # print "Processing defined type"
    dt = i['defined_type']
    o_qname = 'figshare_{}'.format(quote(dt))
            
    a_graph.add((article_uri,LUV['defined_type'],LU[o_qname]))
    a_graph.add((LU[o_qname],SKOS.prefLabel,Literal(dt)))
    a_graph.add((LU[o_qname],RDF.type,LUV['DefinedType']))
    
    # print "Processing published date"
    date = i['published_date']
    pydate = datetime.strptime(date,'%H:%M, %b %d, %Y')
    a_graph.add((article_uri,LUV['published_date'],Literal(pydate)))
    
    # print "Processing description"
    description = i['description']
    a_graph.add((article_uri,SKOS.description, Literal(description)))

    if len(i['authors']) > 0 :
        # print "Processing authors..."
        author_count = 0 
        seq = BNode()
        
        a_graph.add((article_uri,LUV['authors'],seq))
        a_graph.add((seq,RDF.type,RDF.Seq))
        
        for author in i['authors'] :
            a_id = author['id']
            a_label = author['full_name'].strip()
            a_first = author['first_name'].strip()
            a_last = author['last_name'].strip()
            a_qname = 'figshare_{}'.format(a_id)
            
            author_count = author_count + 1
            
            member = URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#_{}'.format(author_count))
            a_graph.add((seq,member,LU[a_qname]))
            a_graph.add((LU[a_qname],FOAF['name'],Literal(a_label)))
            a_graph.add((LU[a_qname],FOAF['firstName'],Literal(a_first)))
            a_graph.add((LU[a_qname],FOAF['lastName'],Literal(a_last)))
            a_graph.add((LU[a_qname],LUV['id'],Literal(a_id)))
            a_graph.add((LU[a_qname],RDF.type,LUV['Author']))
            a_graph.add((LU[a_qname],RDF.type,FOAF['Person']))
    

    
    # print "Processing tags..."
    for tag in i['tags'] :
        # print tag
        
        t_id = tag['id']
        t_label = tag['name']
        t_qname = 'figshare_{}'.format(t_id)

        a_graph.add((article_uri,LUV['tag'],LU[t_qname]))
        a_graph.add((LU[t_qname],SKOS.prefLabel,Literal(t_label)))
        a_graph.add((LU[t_qname],LUV['id'],Literal(t_id)))   
        a_graph.add((LU[t_qname],RDF.type,LUV['Tag']))
        
    # print "Processing links..."
    for link in i['links'] :
        # print link
        l_id = link['id']
        l_value = link['link']
        l_qname = 'figshare_{}'.format(l_id)
        
        a_graph.add((article_uri,LUV['link'],LU[l_qname]))
        a_graph.add((LU[l_qname],LUV['id'],Literal(l_id)))
        a_graph.add((LU[l_qname],RDFS.seeAlso,URIRef(l_value))) 
        a_graph.add((LU[l_qname],FOAF['page'],URIRef(l_value))) 
        a_graph.add((LU[l_qname],RDF.type,LUV['Link']))
        
        # print "Checking if link matches a Wikipedia/DBPedia page..."
        
        if l_value.startswith('http://en.wikipedia.org/wiki/') :
            l_match = re.sub('http://en.wikipedia.org/wiki/','http://dbpedia.org/resource/',l_value)
            a_graph.add((LU[l_qname],SKOS.exactMatch,URIRef(l_match)))
        
    # print "Processing files..."
    for f in i['files'] :
        # print f
        f_id = f['id']
        f_value = f['name']
        f_mime = f['mime_type']
        f_size = f['size']
        f_qname = 'figshare_{}'.format(f_id)
        
        a_graph.add((article_uri,LUV['file'],LU[f_qname]))
        a_graph.add((LU[f_qname],LUV['id'],Literal(f_id)))
        a_graph.add((LU[f_qname],RDFS.label,Literal(f_value))) 
        a_graph.add((LU[f_qname],LUV['mime_type'],Literal(f_mime)))
        a_graph.add((LU[f_qname],LUV['size'],Literal(f_size)))
        a_graph.add((LU[f_qname],RDF.type,LUV['File']))
        
    # print "Processing categories..."
    for cat in i['categories'] :
        # print cat
        c_id = cat['id']
        c_value = cat['name']
        c_qname = 'figshare_{}'.format(c_id)
        
        a_graph.add((article_uri,LUV['category'],LU[c_qname]))
        a_graph.add((LU[c_qname],LUV['id'],Literal(c_id)))
        a_graph.add((LU[c_qname],RDFS.label,Literal(c_value))) 
        a_graph.add((LU[c_qname],RDF.type,LUV['Category']))
    
    
    selected_urls = [u for u in urls if u['uri'] in checked_urls]
    
    
    for u in selected_urls :      
        original_qname = u['original']
        uri = u['uri']
                    
        if u['type'] == 'mapping':
            a_graph.add((LU[original_qname],SKOS.exactMatch,URIRef(uri) ))
        elif u['type'] == 'reference':
            a_graph.add((LU[original_qname],DCTERMS['references'],URIRef(uri) ))
        elif u['type'] == 'link' :
            a_graph.add((LU[original_qname],SKOS.related, URIRef(uri)))
        else :
            a_graph.add((LU[original_qname],SKOS.related, URIRef(uri)))

    graph = ConjunctiveGraph(store)
    
    # out = ""
    # for s, p, o, gr in graph.quads((None, None, None)) :
    #    out += "{} > {} {} {}\n".format(gr.identifier, s, p, o)
    #
    # app.logger.debug(out)


    return graph
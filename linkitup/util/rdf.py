"""

Module:    rdf.py
Author:    Rinke Hoekstra
Created:   2 November 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from flask import g

from rdflib import Graph, ConjunctiveGraph, Namespace, URIRef, Literal, BNode, plugin
from rdflib.store import Store
from rdflib.namespace import RDF, RDFS, SKOS, OWL
from urllib import quote
from datetime import datetime
import re
import os
import string
import requests
from linkitup.util import get_qname
from linkitup import app
from provenance import trail_to_prov

# Override RDFLib trig serializer with app/util/trig.py
# RDFLib serializer still uses the deprecated '=' between graph URI and graph contents
from rdflib.serializer import Serializer
plugin.register('trig', Serializer, 'app.util.trig', 'TrigSerializer')

LUV = Namespace('http://linkitup.data2semantics.org/vocab/')
LU = Namespace('http://linkitup.data2semantics.org/resource/')
DBPEDIA = Namespace('http://dbpedia.org/resource/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
DCTERMS = Namespace('http://purl.org/dc/terms/')
NANOPUB = Namespace('http://www.nanopub.org/nschema#')
PROV = Namespace('http://www.w3.org/ns/prov#')
OA = Namespace('http://www.w3.org/ns/oa#')

graph_store_endpoint = app.config.get('GRAPH_STORE_ENDPOINT')
graph_store_auth_string = app.config.get('GRAPH_STORE_AUTH')
if graph_store_auth_string:
    graph_store_auth = requests.auth.HTTPDigestAuth(*graph_store_auth_string.split(':'))
else:
    graph_store_auth = None

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

def get_trix(article, checked_urls):
    ## Generate the graph with a dummy id for the nanopublication
    graph = get_rdf('dummy', article, checked_urls)

    serializedGraph = graph.serialize(format='trix')
    
    return serializedGraph
   
def get_trig(article, checked_urls, provenance): 
    ## Generate the graph with a dummy id for the nanopublication
    app.logger.info("Using modified RDFLib TriG serializer")
    graph = get_rdf('dummy', article, checked_urls, provenance)
    serializedGraph = graph.serialize(format='trig')
    return serializedGraph

def store_conjunctive_graph(conjunctive_graph):
    """
    Stores the conjunctive_graph using Graph Store HTTP Protocol endpoint ignoring contexts
    which are not identified by an URI.
    """
    if not graph_store_endpoint:
        app.logger.warning("Failed to store the graph: Graph Store endpoint is not defined.")
        return False
    headers =  {'content-type':'application/n-triples;charset=UTF-8'}
    graphs = [g for g in conjunctive_graph.contexts() if isinstance(g.identifier, URIRef)]
    for graph in graphs:
        data = graph.serialize(format='nt')
        graph_url = '{}?graph={}'.format(graph_store_endpoint, graph.identifier)
        app.logger.debug("Uploading to {}.".format(graph_url))
        r = requests.put(graph_url, data = data, headers = headers, auth=graph_store_auth)
        if not r.ok :
            app.logger.warning("Something went wrong: couldn't upload to {}".format(graph_url))
            app.logger.debug(r.content)
            return False
        return True

def get_and_publish_trig(nanopub_id, article, checked_urls):
    # NB: provenance is not included
    graph = get_rdf(nanopub_id, article, checked_urls, [])
    app.logger.debug("Storing to triplestore")
    store_conjunctive_graph(graph)
    data = graph.serialize(format='trig')
    return data

def get_rdf(nanopub_id, article, urls, provenance_trail):
    """Takes everything we know about the article specified in article_id, and builds a simple RDF graph. 
    We only consider the URLs of checkboxes that were selected by the user.
    Returns the RDF graph as a ConjunctiveGraph"""
    
    article_id = article['article_id']
    i = article

    article_id_qname = get_qname(article_id)
    nanopub_id_qname = get_qname(nanopub_id)
    
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
    
    p_graph += trail_to_prov(provenance_trail)
    
    # A bit annoying, but we need both the DOI and the Owner before we can start
    
    if 'doi' in i:
        # If the article has a DOI assigned, we will use it in our RDF rendering
        doi = i['doi']
        
        article_uri = URIRef(doi)
    else :
        # If it doesn't, we'll gues the DOI URI of our own making
        
        doi = "http://dx.doi.org/10.6084/m9.figshare.{}".format(article_id)        
        article_uri = URIRef(doi)
        
    a_graph.add((article_uri,OWL.sameAs,LU[article_id_qname]))
    a_graph.add((article_uri,LUV['doi'],URIRef(doi)))
    
    # print "Processing owner..."
    if 'owner' in i:
        owner = i['owner']
        o_id = owner['id']
        o_label = owner['full_name']
        o_qname = get_qname(o_id)
        
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
    
    nanopub_doi = "http://dx.doi.org/10.6084/m9.figshare.{}".format(nanopub_id)    
    nanopub_uri = URIRef(nanopub_doi)

    np_graph.add((nanopub_uri, OWL.sameAs, LU[nanopub_id_qname]))
    np_graph.add((nano, RDFS['seeAlso'], nanopub_uri))
    
    now = datetime.now()
    nowstr = datetime.now().strftime("%Y%m%dT%H%M%S%z")

    # Add the necessary provenance information
    
    user_qname = re.sub(' ','_', g.user.nickname)
    user_uri = LU['person/{}'.format(user_qname)]
    
    activity_uri = LU['linkitup_{}'.format(nowstr)]
   
    p_graph.add((nano, RDF.type, PROV['Entity']))
    
    p_graph.add((nano, DCTERMS['license'], URIRef('http://creativecommons.org/publicdomain/zero/1.0/')))
    p_graph.add((nano, PROV['wasGeneratedBy'], activity_uri))
    p_graph.add((nano, PROV['wasGeneratedAt'], Literal(now)))
    p_graph.add((nano, PROV['wasAttributedTo'], user_uri))
    
    p_graph.add((activity_uri, RDF.type, PROV['Activity']))
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
    o_qname = get_qname(quote(dt))
            
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
            a_qname = get_qname(a_id)
            
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
        t_qname = get_qname(t_id)

        a_graph.add((article_uri,LUV['tag'],LU[t_qname]))
        a_graph.add((LU[t_qname],SKOS.prefLabel,Literal(t_label)))
        a_graph.add((LU[t_qname],LUV['id'],Literal(t_id)))   
        a_graph.add((LU[t_qname],RDF.type,LUV['Tag']))
        
    # print "Processing links..."
    for link in i['links'] :
        # print link
        l_id = link['id']
        l_value = link['link']
        l_qname = get_qname(l_id)
        
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
        f_qname = get_qname(f_id)
        
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
        c_qname = get_qname(c_id)
        
        a_graph.add((article_uri,LUV['category'],LU[c_qname]))
        a_graph.add((LU[c_qname],LUV['id'],Literal(c_id)))
        a_graph.add((LU[c_qname],RDFS.label,Literal(c_value))) 
        a_graph.add((LU[c_qname],RDF.type,LUV['Category']))
    
    for k,u in urls.items() :      
        original_qname = get_qname(u['original'])
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

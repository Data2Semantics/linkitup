"""

Module:    rdf.py
Author:    Rinke Hoekstra
Created:   2 November 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from flask import session

from rdflib import Graph, Namespace, URIRef, Literal, BNode
from rdflib.namespace import RDF, RDFS, SKOS, OWL
from urllib import quote
from datetime import datetime
import re


def get_rdf(article_id, checked_urls):
    """Takes everything we know about the article specified in article_id, and builds a simple RDF graph. 
    
    We only consider the URLs of checkboxes that were selected by the user.
    
    Returns the RDF graph as a ConjunctiveGraph"""
    

    
    FSV = Namespace('http://figshare.com/vocab/')
    FS = Namespace('http://figshare.com/resource/')
    DBPEDIA = Namespace('http://dbpedia.org/resource/')
    FOAF = Namespace('http://xmlns.com/foaf/0.1/')
    DCTERMS = Namespace('http://purl.org/dc/terms/')
    
    g = Graph(identifier=URIRef('http://www.example.com'))
    g.bind('fsv',FSV)
    g.bind('fs',FS)
    g.bind('skos',SKOS)
    g.bind('dbpedia',DBPEDIA)
    g.bind('foaf',FOAF)
    g.bind('dcterms',DCTERMS)
    
    items = session.get('items',[])
    
    urls = session.get(article_id,[])
        
    i = items[article_id]

    article_id_qname = 'FS{}'.format(article_id)
    
    if 'doi' in i:
        # If the article has a DOI assigned, we will use it in our RDF rendering
        doi = i['doi']
        
        article_uri = URIRef(doi)
        g.add((article_uri,OWL.sameAs,FS[article_id_qname]))
    else :
        # If it doesn't, we'll use a URI of our own making
        article_uri = FS[article_id_qname]
    
    
    
    g.add((article_uri,FSV['article_id'],Literal(article_id)))
    g.add((article_uri,OWL.sameAs,FS[article_id_qname]))
    
    # print "Processing owner..."
    
    if 'owner' in i:
        owner = i['owner']
        o_id = owner['id']
        o_label = owner['full_name']
        o_qname = 'FS{}'.format(o_id)
                
        g.add((article_uri,FSV['owner'],FS[o_qname]))
        g.add((FS[o_qname],FOAF['name'],Literal(o_label)))
        g.add((FS[o_qname],FSV['id'],Literal(o_id)))
        g.add((FS[o_qname],RDF.type,FSV['Owner']))
    
    # print "Processing defined type"
    dt = i['defined_type']
    o_qname = 'FS{}'.format(quote(dt))
            
    g.add((article_uri,FSV['defined_type'],FS[o_qname]))
    g.add((FS[o_qname],SKOS.prefLabel,Literal(dt)))
    g.add((FS[o_qname],RDF.type,FSV['DefinedType']))
    
    # print "Processing published date"
    date = i['published_date']
    pydate = datetime.strptime(date,'%H:%M, %b %d, %Y')
    g.add((article_uri,FSV['published_date'],Literal(pydate)))
    
    # print "Processing description"
    description = i['description']
    g.add((article_uri,SKOS.description, Literal(description)))

    if len(i['authors']) > 0 :
        # print "Processing authors..."
        author_count = 0 
        seq = BNode()
        
        g.add((article_uri,FSV['authors'],seq))
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

        g.add((article_uri,FSV['tag'],FS[t_qname]))
        g.add((FS[t_qname],SKOS.prefLabel,Literal(t_label)))
        g.add((FS[t_qname],FSV['id'],Literal(t_id)))   
        g.add((FS[t_qname],RDF.type,FSV['Tag']))
        
    # print "Processing links..."
    for link in i['links'] :
        # print link
        l_id = link['id']
        l_value = link['link']
        l_qname = 'FS{}'.format(l_id)
        
        g.add((article_uri,FSV['link'],FS[l_qname]))
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
        
        g.add((article_uri,FSV['file'],FS[f_qname]))
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
        
        g.add((article_uri,FSV['category'],FS[c_qname]))
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
        elif u['type'] == 'link' :
            g.add((FS[original_qname],SKOS.related, URIRef(uri)))
        else :
            g.add((FS[original_qname],SKOS.related, URIRef(uri)))

    return g
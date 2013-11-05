from datetime import datetime
import urllib

from flask import g
from app import app

from app.util import get_qname

from rdflib import Graph, URIRef, Literal, BNode, Namespace, plugin
from rdflib.namespace import RDF, RDFS, SKOS, OWL, XSD
from rdflib.serializer import Serializer
import re

PROV = Namespace('http://www.w3.org/ns/prov#')
LUV = Namespace('http://linkitup.data2semantics.org/vocab/')
LU = Namespace('http://linkitup.data2semantics.org/resource/')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')


def register(plugin_slug):
	safe_slug = urllib.quote_plus(plugin_slug)
	
	return Activity(safe_slug)
	
class Activity(object):
	
	def __init__(self, name):
		# Get a UTC timestamp in ISO 8601 format
		now = datetime.utcnow().isoformat()

		graph = self.graph = Graph()
		
		graph.bind('prov', PROV)
		graph.bind('luv',LUV)
		graph.bind('lu',LU)
		graph.bind('foaf',FOAF)

		user_qname = re.sub(' ','_', g.user.nickname)
		self.user_uri = LU['person/{}'.format(user_qname)]

		activity_qname = "activity/{}_{}".format(name, now)
		self.activity_uri = LU[activity_qname]
		
		graph.add((self.activity_uri, RDF.type, PROV['Activity']))
		graph.add((self.activity_uri, PROV['startedAtTime'], Literal(now,datatype=XSD['dateTime'])))
		graph.add((self.activity_uri, PROV['wasInfluencedBy'], URIRef('http://linkitup.data2semantics.org')))
		graph.add((self.activity_uri, PROV['wasStartedBy'], self.user_uri))
		graph.add((self.activity_uri, RDFS['label'], Literal(name)))
		
		graph.add((self.user_uri, RDF.type, PROV['Person']))
		graph.add((self.user_uri, RDF.type, PROV['Agent']))
		graph.add((self.user_uri, RDF.type, FOAF['Person']))
		
		graph.add((URIRef('http://linkitup.data2semantics.org'), RDF.type, PROV['Agent']))
		
	
	def done(self):
		# Get a UTC timestamp in ISO 8601 format
		now = datetime.utcnow().isoformat()

		self.graph.add((self.activity_uri, PROV['endedAtTime'], Literal(now, datatype=XSD['dateTime'])))
		
		return self.serialize()
		
	def serialize(self):
		return self.graph.serialize(format='turtle')
	
	def add_input(self, source, label='', resource_type='uri'):
		
		source_entity_uri = self.new_entity(source, label)
				
		self.graph.add((self.activity_uri, PROV['used'], source_entity_uri))
		
	def add_output(self, target, label='', resource_type='uri'):
		# Get a UTC timestamp in ISO 8601 format
		now = datetime.utcnow().isoformat()
		
		target_entity_uri = self.new_entity(target, label)
		
		self.graph.add((target_entity_uri, PROV['wasGeneratedBy'], self.activity_uri))
		
		
	def new_entity(self, uri, label):
		# Get a UTC timestamp in ISO 8601 format
		now = datetime.utcnow().isoformat()
		
		if uri.startswith('http://') :
			resource_uri = URIRef(uri)
		else :
			
			resource_uri = LU[get_qname(uri)]
			
		resource_entity_uri = LU[urllib.quote_plus("entity/{}_{}".format(label, now), safe="/")]
		
		self.graph.add((resource_uri, RDFS['label'], Literal(label)))
		
		self.graph.add((resource_entity_uri, RDF.type, PROV['Entity']))
		self.graph.add((resource_entity_uri, RDFS['label'], Literal(label)))
		self.graph.add((resource_entity_uri, PROV['wasDerivedFrom'], resource_uri))
		self.graph.add((resource_entity_uri, PROV['wasGeneratedAt'], Literal(now, datatype=XSD['dateTime'])))
		
		
		return resource_entity_uri
	
	
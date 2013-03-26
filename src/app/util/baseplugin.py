'''
Created on 26 Mar 2013

@author: Rinke Hoekstra
'''

from flask import render_template

from SPARQLWrapper import SPARQLWrapper, JSON
import re

from app import app

class SPARQLPlugin(object):
    '''
    This is the basic plugin class used by most Linkitup plugins that connect to a SPARQL endpoint.
    '''


    def __init__(self, endpoint, template, match_type = 'mapping', rewrite_function = None, id_function = lambda x: re.sub('\s','_',x), id_base = 'label'):
        '''
        Constructor
        '''
        app.logger.debug("Initializing SPARQLPlugin...")
        
        self.sparql = SPARQLWrapper(endpoint)
        self.sparql.setReturnFormat(JSON)
        
        # Path to the Jinja2 query template in the templates directory
        self.template = template
        
        if match_type == 'mapping' or match_type == 'reference' :
            self.match_type = match_type
        else :
            raise Exception("The only valid values for 'mapping_type' are 'mapping' and 'reference'.")

        # Function that rewrites URIs into less scary ones
        self.rewrite_function = rewrite_function
        
        # Function that generates strings for use in HTML identifiers
        self.id_function = id_function
        # Basis for the HTML identifiers ('label' or 'uri')
        if id_base == 'label' or id_base == 'uri' :
            self.id_base = id_base
        else :
            raise Exception("The only valid values for 'id_base' are 'label' and 'uri'.")
        
        app.logger.debug("Done")
        
    def match(self, items, property = 'rdfs:label'):
        
        query = render_template(self.template, 
                                items=items, 
                                property=property)
        
        app.logger.debug("Query set to:\n {}".format(query))
        
        self.sparql.setQuery(query)
        
        try :
            app.logger.debug("Calling endpoint")
            
            results = self.sparql.query().convert()
            
            app.logger.debug("Done")
            
            
            matches = [] 
            
            for result in results["results"]["bindings"] :
                match_uri = result["match"]["value"]
                original_id = result["original_id"]["value"]
                original_label = result["original_label"]["value"]
                original_qname = "FS{}".format(original_id)
                
                
                app.logger.debug("Match URI: {}".format(match_uri))
                
                # If we have a rewrite function, apply it to the match uri to obtain a web uri
                # We use this e.g. for converting DBPedia URIs into less scary Wikipedia URIs
                if self.rewrite_function :
                    app.logger.debug("Rewrite function defined...")
                    web_uri = self.rewrite_function(match_uri)
                else :
                    web_uri = match_uri
                
                # If the web URI is too long, we shorten it, otherwise the display URI is the same as the web URI
                if len(web_uri) > 61 :
                    display_uri = web_uri[:29] + "..." + web_uri[-29:]
                else :
                    display_uri = web_uri
                
                # Rewrite the original label or uri to something we can use as a basis for generating HTML identifiers
                if self.id_base == 'label' :
                    id_base = self.id_function(original_label)
                else :
                    id_base = self.id_function(original_id)
                    
    
                    
                # Create the match dictionary
                match = {'type':    self.match_type,
                         'uri':     match_uri,
                         'web':     web_uri,
                         'show':    display_uri,
                         'short':   id_base,
                         'original':original_qname}
                
                # Append it to all matches
                matches.append(match)
        except :
            raise Exception("Endpoint at {} produced unintelligible results. Maybe it's down?".format(self.sparql)) 
        
        return matches
        
'''
Created on 26 Mar 2013

@author: Rinke Hoekstra
'''

from flask import render_template, request, jsonify

from SPARQLWrapper import SPARQLWrapper, JSON
import re
import traceback
import sys

from functools import wraps

from app import app
from app.util import get_qname


def plugin(fields=[], link='match'):
    """
    This function creates a plugin decorator
    
    -- fields: list of (key,id,label) tuples where the key a list of dictionaries to be extracted form the 
               article details, and id, label match keys in those dictionaries.
    -- link:   link type to use, can be anything, as long as the RDF generator understands it.

    This decorator only works if it is called with brackets, i.e. @plugin().
    """
    def plugin_decorator(func):
        """
        Defines a function that extracts article details from the keys in 'fields', and pass it to the plugin
        """
        @wraps(func)
        def plugin_wrapper(*args, **kwargs):
            """
            Extracts article details and pass it to the plugin
            """
            article = request.get_json()
            
            article_id = article['article_id']
            article_title = article['title']
            
            inputs = []
            for field, identifier, label in fields:
                for entries in article[field] :
                    inputs.append({'id': entries[identifier], 'label': entries[label].strip()})
            kwargs.update({'article': {'id': article_id, 'label': article_title}, 'inputs': inputs, 'link': link})
            out = func(*args, **kwargs)
            
            return jsonify(out)
        return plugin_wrapper
    return plugin_decorator


class SPARQLPlugin(object):
    '''
    This is the basic plugin class used by most Linkitup plugins that connect to a SPARQL endpoint.
    '''


    def __init__(self, endpoint, template, match_type = 'mapping', rewrite_function = None, id_function = lambda x: re.sub('\s','_',x), id_base = 'label',all=False):
        '''
        Constructor
        '''
        
        app.logger.debug("Initializing SPARQLPlugin...")
        
        if isinstance(endpoint, list) :
            self.endpoints = endpoint
        else :
            self.endpoints = [endpoint]

        
        # Path to the Jinja2 query template in the templates directory
        self.template = template
        
        # The type of mapping that is produced (mapping for tags/terms/categories/authors, reference for citations)
        if match_type == 'mapping' or match_type == 'reference' or match_type == 'link':
            self.match_type = match_type
        else :
            raise Exception("The only valid values for 'mapping_type' are 'mapping', 'reference' and 'link'.")


        # Function that rewrites URIs into less scary ones
        self.rewrite_function = rewrite_function
        
        # Function that generates strings for use in HTML identifiers
        self.id_function = id_function
        # Basis for the HTML identifiers ('label' or 'uri')
        if id_base == 'label' or id_base == 'uri' :
            self.id_base = id_base
        else :
            raise Exception("The only valid values for 'id_base' are 'label' and 'uri'.")
        
        self.all = all
        
        app.logger.debug("Done")
        
        
    def match(self, items, property = 'rdfs:label'):
        app.logger.debug("Finding matches using a single query")
        
        query = render_template(self.template, 
                                items=items, 
                                property=property)
        
        app.logger.debug("Query set to:\n {}".format(query))
        
        
        
        results = self.run_query(query)
    
        if len(results) > 0 :
            matches = self.process_matches(results)
            return matches
        else :
            return {}
        

    
    def match_separately(self, items, property = 'rdfs:label'):
        app.logger.debug("Finding matches using a separate query for each item")
        
        matches = {}
        for item in items :
            
            query = render_template(self.template, 
                                    item=item, 
                                    property=property)
            
            results = self.run_query(query)
            
            matches.update(self.process_matches(results))
            
        return matches
    
    
    def run_query(self, query):
        all_results = []
        tries = []
        
        app.logger.debug(self.endpoints)

        get_tries = [(endpoint, 'GET') for endpoint in self.endpoints]
        post_tries = [(endpoint, 'POST') for endpoint in self.endpoints]
        
        app.logger.debug(get_tries)
        app.logger.debug(post_tries)
        
        tries.extend(post_tries)
        tries.extend(get_tries)
        
        app.logger.debug(tries)
        for (endpoint, method) in tries :
            try :
                sw = SPARQLWrapper(endpoint)
                sw.setMethod(method)
                sw.setReturnFormat(JSON)
                sw.setQuery(query)
            
                app.logger.debug("Calling endpoint {}".format(endpoint))
            
                # Will give problems if e.g. the GET URI is too long, or the endpoint does not respond within reasonable time.
                results = sw.queryAndConvert()
            
                app.logger.debug("Done")
                
                # Will give problems if the return type is not what we expected (e.g. XML instead of JSON)
                if "results" in results:
                    all_results.extend(results["results"]["bindings"])
                    
                    app.logger.debug("Found {} results".format(len(results)))
                    
            except :

                app.logger.warning("Endpoint at {} did not work as expected. Maybe it's down?".format(endpoint))
                exc_type, exc_value, exc_traceback = sys.exc_info()

                traceback.print_exception(exc_type, exc_value, exc_traceback, limit=2, file=sys.stdout)
                app.logger.debug("Continuing with next endpoint...")
                continue 
            else: 
                if not self.all :
                    app.logger.debug("Finally, after calling {}".format(endpoint))
                    app.logger.debug(all_results)
                    break
                else :
                    app.logger.debug("Continuing with next endpoint... (calling all)")
                    continue

        app.logger.debug("Returning results from run_query")
        app.logger.debug(all_results)   
        return all_results
    
    def process_matches(self, results):
        app.logger.debug("Processing results...")
        matches = {}
        app.logger.debug(results)
        for result in results :
            match_uri = result["match"]["value"]
            original_id = result["original_id"]["value"]
            original_label = result["original_label"]["value"]
            # Won't use the qname for 'original', will use the original_id instead. QNames should be minted in the RDF creator.
            # original_qname = get_qname(original_id)
            
            
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
                
            if 'match_label' in result:
                description = result['match_label']['value']
            else :
                description = original_label

                
            # Create the match dictionary
            match = {'type':    self.match_type,
                     'uri':     match_uri,
                     'web':     web_uri,
                     'show':    display_uri,
                     'short':   id_base,
                     'description':   description,
                     'original':original_id}
            
            # Append it to all matches
            matches[match_uri] = match
            
        app.logger.debug("Returning results from process_matches")
        app.logger.debug(matches)
        return matches
        
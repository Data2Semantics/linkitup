'''
Created on 26 Mar 2013

@author: hoekstra
'''

from flask.ext.login import login_required

import requests
import re
from bs4 import BeautifulSoup

from app import app

from app.util.baseplugin import plugin
from app.util.provenance import provenance


EASY_SEARCH_URL = "https://easy.dans.knaw.nl/ui/"


@app.route('/danseasy', methods=['POST'])
@login_required
@plugin(fields=[('tags','id','name'),('categories','id','name')], link='mapping')
@provenance()
def link_to_dans_easy(*args, **kwargs):
    # Retrieve the article from the decorator
    article_id = kwargs['article']['id']
    match_items = kwargs['inputs']
    app.logger.debug("Running DANS EASY plugin for article {}".format(article_id))
    
    query_string = "".join([ "'{}'".format(match_items[0]['label']) ] + [ " OR '{}'".format(item['label']) for item in match_items[1:]])
    
    app.logger.debug("Query: {}".format(query_string))

    SEARCH_PARAMETERS = "?wicket:bookmarkablePage=:nl.knaw.dans.easy.web.search.pages.PublicSearchResultPage"    
    SEARCH_PARAMETERS = SEARCH_PARAMETERS + "&q=" + query_string
    
    response = requests.get(EASY_SEARCH_URL + SEARCH_PARAMETERS)
    
    app.logger.debug("Query URL: {}".format(response.url))
    
#    app.logger.debug(response.content)
    
    soup = BeautifulSoup(response.content)
        
    matches = {}
    
    hits = soup.find_all('div','searchHit2')

    for h in hits:
        hit = get_detailed_hit(h)
        
        match_uri = hit['uri']
        web_uri = hit['uri']
        display_uri = hit['title']
            
        id_base = re.sub('\:','_',hit['urn'])
        
        if 'Description' in hit :
            description = hit['Description'][:600]
        else :
            description = None
        urn = hit['urn']
        score = "Score: {}%".format(hit['score'])
        original_qname = "figshare_{}".format(article_id)
        
        # Create the match dictionary
        match = {'type':    "link",
                 'uri':     match_uri,
                 'web':     web_uri,
                 'show':    display_uri,
                 'short':   id_base,
                 'description': description, 
                 'extra':   urn,
                 'subscript': score,
                 'original':original_qname}
        
        # Append it to all matches
        matches[match_uri] = match

    # Return the matches
    return matches
        
    
def get_detailed_hit(h):
    hit = {}
    
    onclick = h.div['onclick']
    
    match = re.search(".*window\.location\.href='(?P<href>.*)'.*", onclick)
    if match :
        href = match.group('href')
        
        urn_page = requests.get(EASY_SEARCH_URL + href).content

        m = re.search(".*(?P<urn>urn\:nbn\:.*?)\<", urn_page)
        
        if m :
            urn = m.group('urn')
            hit[u'urn'] = urn
            hit[u'uri'] = "http://www.persistent-identifier.nl/?identifier={}".format(urn)
    
    
    col2 = h.find('div','searchHit-col2')
    
    hit[u'title'] = col2.find('div','searchhitTitle').text
    hit[u'publisher'] = col2.find('div',None).text
    
    if col2.span :
        hit[u'year'] = col2.span.text

    
    col3 = h.find('div','searchHit-col3')
    
    for div in col3.find_all('div') :
        hit[div.contents[0].strip().strip(':')] = div.contents[1].text.strip().strip(',')
        
    footer = h.find('div','searchHit-footer')
    
    hit[u'score'] = footer.div.span.text
    
    for snippet in footer.find_all('div','snippets') :
        hit[snippet.find('span','key').text] = snippet.find('span','').text
        
    return hit
    
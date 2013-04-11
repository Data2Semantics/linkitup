"""

Module:    figshare.py
Author:    Rinke Hoekstra
Created:   2 November 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""
from __future__ import unicode_literals

from flask import request, session, render_template, redirect, url_for, g

from flask.ext.login import login_required

import requests
from requests_oauthlib import OAuth1
from urlparse import parse_qs
from urllib import unquote
import json

from app import app, db, lm, oid


## NB: Code now depends on requests v1.0 and oauth_requests

client_key = 'K9qG70PgROIg8CpZGJlGRg'
client_secret = '0JdZcz5pz0HwyWbeiwsviA'

request_token_url = "http://api.figshare.com/v1/pbl/oauth/request_token"
access_token_url = "http://api.figshare.com/v1/pbl/oauth/access_token"


@app.route('/authorize')
@login_required
def figshare_authorize():
    """ Gets the oauth request authorization URL from the figshare API,
    and renders the form for filling in the PIN code (the oauth verifier)
        
    NB: do not confuse the oauth_token with the oauth_request_token! The request token is needed to request the actual oauth_token.
    """
    try:
        oauth_request_auth_url = get_auth_url()
    
        app.logger.debug("Redirecting to {}".format(oauth_request_auth_url))
        
        return redirect(oauth_request_auth_url)
    
        
    except Exception as e:
        return render_template('error.html',
                               message = e.message,
                               user = g.user)


@app.route('/callback', methods=['GET'])
@login_required
def figshare_validate():
    """ Validates the PIN code provided by the user in the authorization web form,
    and gets the oauth token and secret."""
    
    if request.method == 'GET':
        oauth_verifier = request.args.get('oauth_verifier')
        returned_oauth_token = request.args.get('oauth_token')
        
        if returned_oauth_token != session['resource_owner_key'] :
            return render_template('error.html',
                                   message = "The OAuth verifier returned by Figshare does not match the request token!",
                                   user = g.user )
    else :
        return render_template('error.html',
                               message = "Did not retrieve an OAuth verifier",
                               user = g.user )
    
    app.logger.debug("Retrieved PIN number: {}".format(oauth_verifier))
    
    try:
        validate_oauth_verifier(oauth_verifier)
        return redirect(url_for('dashboard'))
    except Exception as e:
        return render_template('error.html',
                               message = e.message,
                               user = g.user )
    






def get_auth_url():
    """Uses the consumer key and secret to get a token and token secret for requesting authorization from Figshare
    
    Returns the authorization URL, or raises an exception if the response contains an error.
    """
    oauth = OAuth1(client_key, client_secret=client_secret)
    
    
    response = requests.post(url=request_token_url, auth=oauth)
    
    qs = parse_qs(response.content)
    
    if 'error' in qs:
        raise Exception(qs['error'])
    else :     
        resource_owner_key = qs['oauth_token'][0]
        resource_owner_secret = qs['oauth_token_secret'][0]
        oauth_request_auth_url = unquote(qs['oauth_request_auth_url'][0])
    
        session['resource_owner_key'] = resource_owner_key
        session['resource_owner_secret'] = resource_owner_secret
        
        app.logger.debug("get_auth_url(): resource_owner_key = {}".format(resource_owner_key))
        app.logger.debug("get_auth_url(): resource_owner_secret = {}".format(resource_owner_secret))
        
        session.modified = True
        
        return oauth_request_auth_url

def validate_oauth_verifier(oauth_verifier):
    """Retrieves an oauth access token and secret from Figshare using the oauth_verifier (pin) provided by the user. 
    
    Adds the oauth token and secret to the session, or raises an exception if the response is empty or contains an error.
    """
    
    app.logger.debug("Validating OAuth verifier (PIN)")
    
    resource_owner_key = session.get('resource_owner_key')
    resource_owner_secret = session.get('resource_owner_secret')
    
    app.logger.debug("validate_oauth_verifier(): resource_owner_key = {}".format(resource_owner_key))
    app.logger.debug("validate_oauth_verifier(): resource_owner_secret = {}".format(resource_owner_secret))
    
    oauth = OAuth1(client_key,
                   client_secret=client_secret,
                   resource_owner_key=resource_owner_key,
                   resource_owner_secret=resource_owner_secret,
                   verifier=oauth_verifier)
    

    response = requests.post(url=access_token_url, auth=oauth)
    response_content = parse_qs(response.content)
    
    if response_content == {} :
        app.logger.error("Authorization failed")
        raise Exception('Authorization failed')
    elif 'error' in response_content :
        app.logger.error(response_content['error'])
        raise Exception(response_content['error'])
    else :
        app.logger.debug("OAuth verifier validated!")
        
        # Here we make sure that the oauth token, secret and xoauth figshare id are stored with the user entry in the database.
        g.user.oauth_token = response_content['oauth_token'][0]
        g.user.oauth_token_secret = response_content['oauth_token_secret'][0]
        g.user.xoauth_figshare_id = response_content['xoauth_figshare_id'][0]
        
        app.logger.debug("Token : {}".format(response_content['oauth_token'][0]))
        app.logger.debug("Secret: {}".format(response_content['oauth_token_secret'][0]))
        app.logger.debug("ID    : {}".format(response_content['xoauth_figshare_id'][0]))
        
        db.session.commit()
    return


def get_articles():
    """Uses the oauth token and secret to obtain all articles of the authenticated user from Figshare
    
    Adds the results to the session under 'items', or raises an exception if the response contains an error.
    """
    
    app.logger.debug("Retrieving all articles owned by the user.")
    
    oauth_token = g.user.oauth_token
    oauth_token_secret = g.user.oauth_token_secret


    app.logger.debug("Token : {}".format(g.user.oauth_token))
    app.logger.debug("Secret: {}".format(g.user.oauth_token_secret))

    oauth = OAuth1(client_key,
                   client_secret=client_secret,
                   resource_owner_key=oauth_token,
                   resource_owner_secret=oauth_token_secret)

    
    # We'll start at page 0, will be updated at the start of the first loop.
    page = 0
    
    # Make sure to reset the items in the session (otherwise the session keeps on increasing with every call to this function)
    # TODO: this currently happens for every page refresh on the dashboard, and that might be a bit overkill
    session['items'] = {}
    session.modified = True

    while True:
        page += 1
        params = {'page': page}
        
        response = requests.get(url='http://api.figshare.com/v1/my_data/articles',auth=oauth, params=params)
        app.logger.debug("Called: {}".format(response.url))
        
        results = json.loads(response.content)
        
        if 'error' in results:
            app.logger.error(results)
            if results['error'] == 'No valid token could be found' :
                raise FigshareNoTokenError(results['error'])
            else :
                raise Exception(results['error'])
        elif results == {} :
            app.logger.error("No articles found, retrieved empty response. This probably means that we have an OAuth issue.")
            raise FigshareEmptyResponse("No articles found, retrieved empty response. This probably means that we have an OAuth issue.")
        else :
            if len(results['items']) == 0:
                print "No more results"
                break
            else :
                # Add all articles in results['items'] (a list) to the session['items'] dictionary, to improve lookup.
                for article in results['items'] :
                    session['items'][str(article['article_id'])] = article

                session.modified = True
    
    return


def update_article(article_id, checked_urls):
    
    article_urls = session.get(article_id,[])
    
    oauth_token = g.user.oauth_token
    oauth_token_secret = g.user.oauth_token_secret


    oauth = OAuth1(client_key,
                   client_secret=client_secret,
                   resource_owner_key=oauth_token,
                   resource_owner_secret=oauth_token_secret)
        
    
    print "Checked urls: ", checked_urls
    for u in article_urls :
        if u['uri'] in checked_urls :
            body = {'link': u['web']}
            headers = {'content-type':'application/json'}
        
            response = requests.put('http://api.figshare.com/v1/my_data/articles/{}/links'.format(article_id),
                                data=json.dumps(body), headers=headers, auth=oauth)
            results = json.loads(response.content)
            print "Added {} with the following results:\n".format(u['uri']), results
    
    body = {'tag_name': 'Enriched with LinkItUp'}
    headers = {'content-type':'application/json'}
        
    response = requests.put('http://api.figshare.com/v1/my_data/articles/{}/tags'.format(article_id),
                                data=json.dumps(body), headers=headers, auth=oauth)
    
    
    return
    


class FigshareEmptyResponse(Exception):
    pass

class FigshareNoTokenError(Exception):
    pass



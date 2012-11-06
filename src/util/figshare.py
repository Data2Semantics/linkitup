"""

Module:    figshare.py
Author:    Rinke Hoekstra
Created:   2 November 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""

import requests
from oauth_hook import OAuthHook
from time import time
from urlparse import parse_qs
from urllib import unquote
import json
import random
import string

OAuthHook.consumer_key = 'K9qG70PgROIg8CpZGJlGRg'
OAuthHook.consumer_secret = '0JdZcz5pz0HwyWbeiwsviA'



def get_auth_url(request):
    """Uses the consumer key and secret to get a token and token secret for requesting authorization from Figshare
    
    Returns the authorization URL, or raises an exception if the response contains an error.
    """
    figshare_oauth_hook = OAuthHook(header_auth=True)
    
    response = requests.post('http://api.figshare.com/v1/pbl/oauth/request_token', hooks={'pre_request': figshare_oauth_hook})
    
    qs = parse_qs(response.content)
    
    if 'error' in qs:
        raise Exception(qs['error'])
    else :     
        oauth_request_token = qs['oauth_token'][0]
        oauth_request_token_secret = qs['oauth_token_secret'][0]
        oauth_request_auth_url = unquote(qs['oauth_request_auth_url'][0])
    
        request.session['oauth_request_token'] = oauth_request_token
        request.session['oauth_request_token_secret'] = oauth_request_token_secret
        
        return oauth_request_auth_url

def validate_oauth_verifier(request, oauth_verifier):
    """Retrieves an oauth access token and secret from Figshare using the oauth_verifier (pin) provided by the user. 
    
    Adds the oauth token and secret to the session, or raises an exception if the response is empty or contains an error.
    """
    oauth_request_token = request.session.get('oauth_request_token')
    oauth_request_token_secret = request.session.get('oauth_request_token_secret')
    
    figshare_oauth_hook = OAuthHook(oauth_request_token, oauth_request_token_secret, header_auth=True)
    response = requests.post('http://api.figshare.com/v1/pbl/oauth/access_token', {'oauth_verifier': oauth_verifier}, hooks={'pre_request': figshare_oauth_hook})
    response_content = parse_qs(response.content)
    
    if response_content == {} :
        raise Exception('Authorization failed')
    elif 'error' in response_content :
        raise Exception(response_content['error'])
    else :
        oauth_token = response_content['oauth_token'][0]
        oauth_token_secret = response_content['oauth_token_secret'][0]
        xoauth_figshare_id = response_content['xoauth_figshare_id'][0]
    
        request.session['oauth_token'] = oauth_token
        request.session['oauth_token_secret'] = oauth_token_secret
        request.session['xoauth_figshare_id'] = xoauth_figshare_id
    
    return


def get_articles(request):
    """Uses the oauth token and secret to obtain all articles of the authenticated user from Figshare
    
    Adds the results to the session under 'items', or raises an exception if the response contains an error.
    """
    oauth_token = request.session.get('oauth_token')
    oauth_token_secret = request.session.get('oauth_token_secret')

    oauth_hook = OAuthHook(oauth_token, oauth_token_secret, header_auth=True)

    client = requests.session(hooks={'pre_request': oauth_hook})

    response = client.get('http://api.figshare.com/v1/my_data/articles')

    if 'error' in response.content :
        raise Exception(response['error'])
    else :
        results = json.loads(response.content)
        
        request.session['items'] = results['items']
        request.session.modified = True
    
    return results






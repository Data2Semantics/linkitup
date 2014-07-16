import urllib
import requests

API_URL = 'http://preflabel.org/api'
label_url = '{}/label/'.format(API_URL)

def label(uri):
    url = label_url + urllib.quote(uri, safe='')
    r = requests.get(url)
    if r.ok:
        return r.json()['label']
    return None

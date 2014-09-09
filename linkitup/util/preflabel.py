import urllib
import requests

API_URL = 'http://preflabel.org/api/v1'
label_url = '{}/label/'.format(API_URL)


def label(uri, fallback=False):
    url = label_url + urllib.quote(uri, safe='')
    r = requests.get(url, headers={'Accept': 'application/json'})
    if r.ok:
        return r.json()['label']
    return uri if fallback else None

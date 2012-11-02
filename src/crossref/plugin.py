'''
Created on 2 Oct 2012

@author: hoekstra
'''
from django.http import HttpResponse
from django.shortcuts import render_to_response
import json
import requests
import urllib
from extract import extract_references
import re

def linkup(request, article_id):
    items = request.session.get('items',[])
    
    for i in items :
        if str(i['article_id']) == str(article_id) :
            
            # Only applicable to PDF files
            files = [f for f in i['files'] if f['mime_type'] == 'application/pdf']
            
            if len(files) > 0:
                return render_to_response('crossref.html',{'title':'Crossref','files': files, 'article_id': article_id})
            
                
    
    return render_to_response('message.html',{'type': 'error', 'text': 'This dataset does not contain any PDF files'})


def upload(request, article_id, file_id):
    print article_id, file_id
    print request.FILES
    
    if 'files[]' in request.FILES :
        result = [{'name': request.FILES['files[]'].name}]
        
        tempfile = request.FILES['files[]'].temporary_file_path()
        print 'upload: tempfile', tempfile
        
        request.session.setdefault('files',{})[file_id] = tempfile
        request.session.modified = True
        
        print 'upload: files', request.session['files']
        
        result = [  {
            "name":"{}.pdf".format(file_id)
        }]
        print result
        
        return HttpResponse(json.dumps(result))
    
    else :
        result = [{'name': 'Something went wrong ...'}]
        return HttpResponse(json.dumps(result), mimetype="application/json")
    
def extract(request, article_id, file_id):
    print 'extract: files', request.session.get('files')

    tempfile = request.session['files'][file_id]
    print 'extract: files_file_id (tempfile)', tempfile
    
#### THE CODE BELOW IS FOR USE WITH CROSSREF PDF-EXTRACT (If you manage to get it running on your system)
#    output = subprocess.check_output(['pdf-extract','extract','--references',tempfile])
#    print output
#    
#    root = et.fromstring(output)
#    
#    references = []
#    
#    for child in root :
#        references.append({'id': child.attrib['order'], 'text': child.text})
####

    # Use the custom reference extraction function from the bundled extract.py script
    references = extract_references(tempfile)
        
    return render_to_response('references.html',{'article_id': article_id, 'file_id': file_id, 'references': references})

def match(request, article_id, file_id):
    # CrossRef search http://crossref.org/sigg/sigg/FindWorks?version=1&access=API_KEY&format=json&op=OR&expression=allen+renear
    text = urllib.unquote(request.GET['text'])

    data = {'version': 1,
            'access': 'API_KEY',
            'format': 'json',
            'op': 'OR',
            'expression': text
            }
    
    r = requests.get('http://crossref.org/sigg/sigg/FindWorks', params=data)
    
    results = json.loads(r.text)
    
    
    urls = []
    for r in results[0:3]:
        uri = 'http://dx.doi.org/{}'.format(r['doi'])
        
        short = re.sub('\.|/','_',r['doi'])
        
        
        urls.append({'type': 'reference', 'uri': uri, 'web': uri, 'show': r['fullCitation'], 'short': short, 'original': 'FS{}'.format(file_id)})
    
    
    request.session.setdefault(article_id,[]).extend(urls)
    request.session.modified = True
    
    if urls == []:
        urls = None
    
    return render_to_response('crossref_urls.html',{'urls': urls})
    
    
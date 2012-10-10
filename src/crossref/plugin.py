'''
Created on 2 Oct 2012

@author: hoekstra
'''
from django.http import HttpResponse
from django.shortcuts import render_to_response
import json
import subprocess
import xml.etree.ElementTree as et

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
    output = subprocess.check_output(['pdf-extract','extract','--references',tempfile])
    print output
    
    root = et.fromstring(output)
    
    references = []
    
    for child in root :
        references.append({'id': child.attrib['order'], 'text': child.text})
        
    return render_to_response('references.html',{'article_id': article_id, 'file_id': file_id, 'references': references})

def match(request):
    # CrossRef search http://crossref.org/sigg/sigg/FindWorks?version=1&access=API_KEY&format=json&op=OR&expression=allen+renear
    print request.GET['text']
    
    return HttpResponse('blaa');
    
    
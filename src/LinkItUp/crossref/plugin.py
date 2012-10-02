'''
Created on 2 Oct 2012

@author: hoekstra
'''
from django.http import HttpResponse
from django.shortcuts import render_to_response


def linkup(request, article_id):
    return render_to_response('message.html',{'type': 'error', 'text': 'Linking to CrossRef is not yet implemented, sorry!'})

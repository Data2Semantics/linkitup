"""

Module:    urls.py
Author:    Rinke Hoekstra
Created:   22 September 2012

Copyright (c) 2012, Rinke Hoekstra, VU University Amsterdam 
http://github.com/Data2Semantics/linkitup

"""

from django.conf.urls.defaults import patterns, url, include


urlpatterns = patterns('',
    url(r'^favicon\.ico$', 'django.views.generic.simple.redirect_to', {'url': '/static/img/favicon.ico'}),
    url(r'^$', 'views.index', name='index'),
    url(r'^dashboard$', 'views.dashboard', name='dashboard'),
    url(r'^authorize', 'views.authorize', name='authorize'),
    url(r'^validate', 'views.validate', name='validate'),
    url(r'^clear$', 'views.clear', name='clear'),
#    url(r'^linkup/(?P<article_id>\d+)$', 'views.linkup', name='linkup'),
#    url(r'^process/(?P<article_id>\d+)$', 'views.process', name='process'),
    
    url(r'^dbpedia/(?P<article_id>\d+)$', 'dbpedia.plugin.linkup', name='dbpedia'),
    url(r'^dblp/(?P<article_id>\d+)$', 'dblp.plugin.linkup', name='dblp'),
    url(r'^ldr/(?P<article_id>\d+)$', 'ldr.plugin.linkup', name='ldr'),
    url(r'^orcid/(?P<article_id>\d+)$', 'orcid.plugin.linkup', name='orcid'),
    url(r'^crossref/(?P<article_id>\d+)$', 'crossref.plugin.linkup', name='crossref'),
    url(r'^crossref/upload/(?P<article_id>\d+)/(?P<file_id>\d+)$', 'crossref.plugin.upload', name='upload'),
    url(r'^crossref/extract/(?P<article_id>\d+)/(?P<file_id>\d+)$', 'crossref.plugin.extract', name='extract'),
    url(r'^crossref/match/(?P<article_id>\d+)/(?P<file_id>\d+)$', 'crossref.plugin.match', name='match'),

)


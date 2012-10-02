from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'LinkItUp.views.index', name='index'),
    url(r'^pin$', 'LinkItUp.views.pin', name='pin'),
    url(r'^clear$', 'LinkItUp.views.clear', name='clear'),
    url(r'^linkup/(?P<article_id>\d+)$', 'LinkItUp.views.linkup', name='linkup'),
    url(r'^process/(?P<article_id>\d+)$', 'LinkItUp.views.process', name='process'),
    
    url(r'^dbpedia/(?P<article_id>\d+)$', 'LinkItUp.dbpedia.plugin.linkup', name='dbpedia'),
    url(r'^dblp/(?P<article_id>\d+)$', 'LinkItUp.dblp.plugin.linkup', name='dblp'),
    url(r'^crossref/(?P<article_id>\d+)$', 'LinkItUp.crossref.plugin.linkup', name='crossref'),
    
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)


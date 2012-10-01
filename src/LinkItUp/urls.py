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
    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)


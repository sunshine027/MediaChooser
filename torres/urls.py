#! /usr/bin/env python
#coding=utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('MediaChooser.torres.views',
    (r'^track/$', 'track'),
    (r'^summary/$', 'summary',{'template':'summary.html'}),
    (r'^test/$', 'test',{'template':'test_page.html'}),
)

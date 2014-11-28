#! /usr/bin/env python
#coding=utf-8

from django.conf.urls.defaults import *

from MediaChooser.media_planning.views import *

urlpatterns = patterns('',
    (r'^upload/$', upload),
    (r'^my-uploads/$', my_uploads),
    (r'^uploads-checkout/$', uploads_checkout),
)

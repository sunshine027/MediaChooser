#! /usr/bin/env python
#coding=utf-8

from django.conf.urls.defaults import *

from MediaChooser.client.views import *

urlpatterns = patterns('',
    (r'^create-client/$', create_client),
)

#! /usr/bin/env python
#coding=utf-8

from django.conf.urls.defaults import *

from MediaChooser.media.views import *

urlpatterns = patterns('',
    (r'^info/$', get_mediainfo),
)

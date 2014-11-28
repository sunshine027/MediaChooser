#! /usr/bin/env python
#coding=utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('MediaChooser.NielsenMedia.views',
    (r'^$', 'rank', {'template':'nielsen_media/nielsen_rank.html'}),
    (r'^traffic/$', 'traffic', {'template':'nielsen_media/nielsen_traffic.html'}),
    (r'^overlap/$', 'overlap', {'template':'nielsen_media/nielsen_overlap.html'}),
    (r'^chart/$', 'chart'),
    # Ajax
    (r'^get_media_options/$', 'get_media_options'),
    (r'^get_overlap_data/$', 'get_overlap_data'),
)

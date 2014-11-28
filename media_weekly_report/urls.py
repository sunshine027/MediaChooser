#! /usr/bin/env python
#coding=utf-8

from django.conf.urls.defaults import *

from MediaChooser.media_weekly_report.views import *

urlpatterns = patterns('',
    (r'^create-reportitem/$', create_reportitem),
    # create or modify report items
    (r'^reportitem/$', reportitem),
    (r'^get-subtypes/$', get_subtypes),
    (r'^create-project/$', create_project),
    (r'^get-projects/$', get_projects),
    (r'^delete-report/$', delete_report),
    (r'^modify-report/$', modify_report),
    (r'^get-report/$', get_report),
    (r'^get-statics/$', get_statics),
    (r'^get-statics-xls/$', get_statics_xls),
    (r'^chart_demo/$', chartdemo),
    (r'^ofc_json_data/(.+)$', ofc_response),
)

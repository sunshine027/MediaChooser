#! /usr/bin/env python
#coding=utf-8

from django.conf.urls.defaults import *

urlpatterns = patterns('MediaChooser.ad_resource_mgmt.views',
    url(r'^$', 'query', name="query"),
    (r'^search/$', 'search'),
    
    (r'^query_mflights/$', 'query_mflights'),
    (r'^mflights/$', 'mflights'),
    (r'^query_media/$', 'query_media'),
    url(r'^campaign/(?P<campaign_id>\d+)/$', 'get_campaign', name='get_campaign'),
    url(r'^campaign/status/(?P<ad_id>\d+)/$', 'get_campaign_status', name='get_campaign_status'),
#    url(r'^campaign/(?P<campaign_id>\d+)/export/$', 'campaign_export', name='campaign_export'),
    url(r'^campaign_detail/(?P<campaign_id>\d+)/$', 'get_campaign_detail', name='get_campaign_detail'),
    url(r'^campaign_detail/(?P<campaign_id>\d+)/date_cpc/$', 'get_campaign_detail_date_cpc', name='get_campaign_detail_date_cpc'),
    url(r'^campaign_detail/(?P<campaign_id>\d+)/media_cpc/$', 'get_campaign_detail_media_cpc', name='get_campaign_detail_media_cpc'),
    url(r'^campaign_detail/(?P<campaign_id>\d+)/price_media/$', 'get_campaign_detail_price_media', name='get_campaign_detail_price_media'),
    url(r'^campaign_detail/(?P<campaign_id>\d+)/funnel/$', 'get_campaign_detail_funnel', name='get_campaign_detail_funnel'),
    url(r'^media_filter/$', 'media_filter', name="media_filter"),
    url(r'^media_reco/$', 'media_reco', name="media_reco"),
    
    (r'^get_mediatree/$', 'get_mediatree'),
    (r'^get_mediatree_chart/$', 'get_mediatree_chart'),
    url(r'^get_mediatree_chart_fusionchart/$', 'get_mediatree_chart_fusionchart', name='get_mediatree_chart_fusionchart'),
    (r'^get_mediareco/$', 'get_mediareco'),
    (r'^get_mediacats/$', 'get_mediacats'),
    url(r'^upload_creative/$', 'upload_creative', name="upload_creative"),
    url(r'^upload_creative/del/$', 'delete_upload_creative', name="delete_upload_creative"),
    url(r'^update_background_code/$', 'update_background_code', name="update_background_code"),
    (r'^media_reco/', 'media_reco'),
    (r'^change_flightname/', 'change_flightname'),
    url(r'^get_campaign_xls/(?P<campaign_id>\d+)/funel/', 'get_campaign_funel_xls', name='get_campaign_funel_xls'),
    url(r'^get_campaign_xls/(?P<campaign_id>\d+)/media_cpc/', 'get_campaign_media_cpc_xls', name='get_campaign_media_cpc_xls'),
    url(r'^get_campaign_xls/(?P<campaign_id>\d+)/media_price/', 'get_campaign_media_price_xls', name='get_campaign_media_price_xls'),
    url(r'^get_campaign_xls/(?P<campaign_id>\d+)/', 'get_campaign_xls', name='get_campaign_xls'),
    
    url(r'^chart_api/(?P<campaign_id>\d+)/(?P<chart_id>\w+)/', 'chart_api', name='get_chart_api'),
    url(r'^chart_api/image/export/', 'export_chart_image', name='export_chart_image'),
    
    
    #(r'^get_test_amdata/', 'get_test_amdata'),
    #(r'^get_test_amcolumn/', 'get_test_amcolumn'),
)

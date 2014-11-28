#coding=utf-8

from django.conf.urls.defaults import *

urlpatterns=patterns('MediaChooser.pr.views',
    url(r'^whole_media_resource/list/$', 'list_whole_media_resource', name='list_whole_media_resource'),
    url(r'^media_resource/add/$', 'add_media_resource', name='add_media_resource'),
    url(r'^media_resource/batch_add/excel/$', 'batch_add_media_resource_by_excel', name='batch_add_media_resource_by_excel'),
    url(r'^media_resource/list/$', 'list_media_resource', name='list_media_resource'),
    url(r'^update_media_resource/list/$', 'list_update_media_resource', name='list_update_media_resource'),
    url(r'^search_media_resource/list/$', 'list_search_media_resource', name='list_search_media_resource'),
    url(r'^media_resource/(?P<media_resource_id>\d+)/edit/$', 'edit_media_resource', name='edit_media_resource'),
    url(r'^media_resource/(?P<media_resource_id>\d+)/delete/$', 'delete_media_resource', name='delete_media_resource'),
    
    url(r'^human_resource_by_media/list/$', 'list_human_resource_by_media', name='list_human_resource_by_media'),
    url(r'^whole_human_resource/list/$', 'list_whole_human_resource', name='list_whole_human_resource'),
    url(r'^search_human_resource/list/$', 'list_search_human_resource', name='list_search_human_resource'),
    
    url(r'^reporter/add/$', 'add_reporter', name='add_reporter'),
    url(r'^reporter/batch_add/excel/$', 'batch_add_reporter_by_excel', name='batch_add_reporter_by_excel'),
    url(r'^reporter/list/$', 'list_reporter', name='list_reporter'),
    url(r'^update_reporter/list/$', 'list_update_reporter', name='list_update_reporter'),
    url(r'^reporter/(?P<reporter_id>\d+)/edit/$', 'edit_reporter', name='edit_reporter'),
    url(r'^reporter/(?P<reporter_id>\d+)/delete/$', 'delete_reporter', name='delete_reporter'),
    
    url(r'^blog_owner/add/$', 'add_blog_owner', name='add_blog_owner'),
    url(r'^blog_owner/batch_add/excel/$', 'batch_add_blog_owner_by_excel', name='batch_add_blog_owner_by_excel'),
    url(r'^blog_owner/list/$', 'list_blog_owner', name='list_blog_owner'),
    url(r'^update_blog_owner/list/$', 'list_update_blog_owner', name='list_update_blog_owner'),
    url(r'^blog_owner/(?P<blog_owner_id>\d+)/edit/$', 'edit_blog_owner', name='edit_blog_owner'),
    url(r'^blog_owner/(?P<blog_owner_id>\d+)/delete/$', 'delete_blog_owner', name='delete_blog_owner'),
    
    url(r'^moderator/add/$', 'add_moderator', name='add_moderator'),
    url(r'^moderator/batch_add/excel/$', 'batch_add_moderator_by_excel', name='batch_add_moderator_by_excel'),
    url(r'^moderator/list/$', 'list_moderator', name='list_moderator'),
    url(r'^update_moderator/list/$', 'list_update_moderator', name='list_update_moderator'),
    url(r'^moderator/(?P<moderator_id>\d+)/edit/$', 'edit_moderator', name='edit_moderator'),
    url(r'^moderator/(?P<moderator_id>\d+)/delete/$', 'delete_moderator', name='delete_moderator'),
    
    url(r'^other_resource/add/$', 'add_other_resource', name='add_other_resource'),
    url(r'^other_resource/list/$', 'list_other_resource', name='list_other_resource'),
    url(r'^update_other_resource/list/$', 'list_update_other_resource', name='list_update_other_resource'),
    url(r'^other_resource/(?P<other_resource_id>\d+)/edit/$', 'edit_other_resource', name='edit_other_resource'),
    url(r'^other_resource/(?P<other_resource_id>\d+)/delete/$', 'delete_other_resource', name='delete_other_resource'),
    
    url(r'^cooperate_resource/add/$', 'add_cooperate_resource', name='add_cooperate_resource'),
    url(r'^cooperate_resource/batch_add/excel/$', 'batch_add_cooperate_resource_by_excel', name='batch_add_cooperate_resource_by_excel'),
    url(r'^cooperate_resource/list/$', 'list_cooperate_resource', name='list_cooperate_resource'),
    url(r'^cooperate_resource/(?P<cooperate_resource_id>\d+)/edit/$', 'edit_cooperate_resource', name='edit_cooperate_resource'),
    url(r'^cooperate_resource/(?P<cooperate_resource_id>\d+)/delete/$', 'delete_cooperate_resource', name='delete_cooperate_resource'),
)
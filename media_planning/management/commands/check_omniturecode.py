#! /usr/bin/env python
#coding=utf-8

from MediaChooser.ad.models import Ad
from MediaChooser.media_planning.models import Flight, DE_ClickData
from MediaChooser.media_planning.views import check_omniturecode
from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage
from django.conf import settings
import pyodbc
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

today = datetime.date.today()
nosc_urls_dict, cantopen_url_dict = check_omniturecode(today)

# mail2note = ['zhaoxiaofan@and-c.com', 'wang_le@and-c.com']
# mail2note = ['ludanfeng@and-c.com']

if len(nosc_urls_dict) > 0:
    html_content = '<h3>今日，以下URL中无Omniture监测代码，请及时查找原因！</h3>'
    for url in nosc_urls_dict:
        html_content += '<p>' + str(url) + '</p>'
        html_content += '<ul>'
        for flight in nosc_urls_dict[url]:
            html_content += '<li>' + flight.ad.name.encode('utf8') + ': ' + flight.media.c_name.encode('utf8') + '->' + flight.channel.c_name.encode('utf8') + '->' + flight.media_ad_info.adform.encode('utf8') + '</li>'
        html_content += '</ul>'
else:
    html_content = '<h3>今日，所有投放的联想广告所对应的landing page都添加了Omniture监测代码！</h3>'

if len(cantopen_url_dict) > 0:
    html_content += '今日，以下广告投放的landing page无法打开：'
    for url in cantopen_url_dict:
        html_content += '<p>' + str(url) + '</p>'
        html_content += '<ul>'
        for flight in cantopen_url_dict[url]:
            html_content += '<li>' + flight.ad.name.encode('utf8') + ': ' + flight.media.c_name.encode('utf8') + '->' + flight.channel.c_name.encode('utf8') + '->' + flight.media_ad_info.adform.encode('utf8') + '</li>'
        html_content += '</ul>'
        
msg = EmailMessage('以下联想广告目标页无Omniture监测代码', html_content, 'andc-it@and-c.com', settings.CHECK_OMNITURECODE_MAIL_LIST)
msg.content_subtype = 'html'
msg.send()

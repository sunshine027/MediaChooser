#! /usr/bin/env python
#coding=utf-8

from MediaChooser.ad.models import Ad
from MediaChooser.media_planning.models import Flight, DE_ClickData
from MediaChooser.media_planning.views import check_omniturecode
from MediaChooser.user_behaviour.models import UserBehaviour
from django.core.management.base import BaseCommand
from django.core.mail import EmailMessage, send_mail
from django.core.exceptions import MultipleObjectsReturned
from django.conf import settings
import pyodbc
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

# Checkout if there existed omniture user behaviour data of yesterday
# If not, notify donglei
yesterday = datetime.date.today() - datetime.timedelta(1)
ubs = UserBehaviour.objects.filter(startdate = yesterday)

if len(ubs) == 0:
    send_mail('今日无SiteCatalyst数据导入MC', 'RT，请查找原因！', 'andc-it@and-c.com', ['donglei@and-c.com', 'zhaoxiaofan@and-c.com'])
else:
    # Get planned flights list A for yesterday
    planned_flights = DE_ClickData.objects.filter(if_planned_spending = True, date = yesterday)
    planned_tc_set = set()
    for cd in planned_flights:
        if cd.ad.client_id == 1:
            planned_tc_set.add(cd.flight.DE_ad_id)

    # Get tracking code list B of such flights which Omniture caught their visiting data yesterday
    ub_tc_set = set()
    for ub in ubs:
        ub_tc_set.add(int(ub.tracking_code))

    # Compare above two lists, if there A is not included in B, then issue notification
    untracked_set = planned_tc_set.difference(ub_tc_set)

    if len(untracked_set) == 0:
        send_mail('昨天预定投放的联想广告都有数据进入至Omniture', 'RT, 请放心！', 'andc-it@and-c.com', ['wangle@and-c.com', 'zhaoxiaofan@and-c.com'])
    else:
        html_content = '如下预定投放的广告位无Omniture数据：'
        html_content += '<ul>'
        for tc in sorted(untracked_set):
            try:
                flight = Flight.objects.get(DE_ad_id = tc)
                html_content += '<li>' + flight.ad.name.encode('utf-8') + '<br />' + flight.media.c_name.encode('utf-8') + ' ' + flight.channel.c_name.encode('utf-8') + ' ' + flight.media_ad_info.adform.encode('utf-8') + ' ngAdID:' + str(tc) + '<br />' + flight.DE_backend_url.encode('utf-8') + '</li><br />'
            except MultipleObjectsReturned:
                html_content += '<li>ngAdID:' + str(tc) + ' 在MC数据库中出现>1次，请联系相关人员查找问题所在</li>'

        # msg = EmailMessage('以下广告位今日无Omniture数据', html_content, 'andc-it@and-c.com', ['wang_le@and-c.com', 'zhaoxiaofan@and-c.com', 'ludanfeng@and-c.com'])
        msg = EmailMessage('以下广告位今日无Omniture数据', html_content, 'andc-it@and-c.com', settings.CHECK_OMNITUREDATA_MAIL_LIST)
        msg.content_subtype = 'html'
        msg.send()

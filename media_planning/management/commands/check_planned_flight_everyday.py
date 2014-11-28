#! /usr/bin/env python
#coding=utf-8

# Check if there r effecient clicks tracked on the day flight planned to advertise.

from MediaChooser.ad.models import Ad
from MediaChooser.media_planning.models import Flight, DE_ClickData
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import EmailMessage
import pyodbc
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

clicks_2track = DE_ClickData.objects.filter(date=datetime.date.today())
planned_flights_set = set()
planned_flights_dict = {}
for click in clicks_2track:
    planned_flights_set.add(click.flight.DE_flight_id)
    planned_flights_dict[click.flight.DE_flight_id] = click.flight

# Get current click data from ng_sum_fixed_c table
de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')

flights_updated = set()
flights_clicks_tracked = {}

sql = 'select flightid, sum(eventcount) from admanager65.ng_sum_fixed_c where startdate=to_date(\'%s\', \'YYYY-MM-DD\') and eventtype=4 group by flightid' % datetime.date.today()
de_cursor = de_db.cursor()
de_cursor.execute(sql)
for row in de_cursor:
    eventcount = int(row[1]*settings.CLICK_COMPENSATION_COEFFICIENT)
    flights_clicks_tracked[row[0]] = eventcount
    if eventcount > settings.USEFUL_CLICK_NUMBER:
        flights_updated.add(row[0])
        
de_cursor.close()

flights_2notify = planned_flights_set.difference(flights_updated)

# Get related ads
ads_2notify_dict = {}
for flight in flights_2notify:
    if ads_2notify_dict.has_key(planned_flights_dict[flight].ad):
        ads_2notify_dict[planned_flights_dict[flight].ad].append(planned_flights_dict[flight])
    else:
        ads_2notify_dict[planned_flights_dict[flight].ad] = [planned_flights_dict[flight]]

# Get related staff
staff_2notify_dict = {}
for ad in ads_2notify_dict:
    for st in ad.related_staff.all():
        if staff_2notify_dict.has_key(st):
            staff_2notify_dict[st][ad] = ads_2notify_dict[ad]
        else:
            staff_2notify_dict[st] = {ad:ads_2notify_dict[ad]}

ldf_mail = 'ludanfeng@and-c.com'
# cc = ['hanping@and-c.com', 'wang_le@and-c.com', 'zhaoxiaofan@and-c.com']

for staff in staff_2notify_dict:
    html_content = '<h3>今日，以下预定投放广告位没有监测到点击数据，请查找原因：</h3>'
    html_content += '<p>可能存在原因：换点位，加码错误，网站广告未上线等</p>'
    uploaders = set()
    lenovo_related = False
    for ad in staff_2notify_dict[staff]:
        # check out if ad is related to lenovo
        lenovo_related = True if ad.client_id == 1 else lenovo_related
        html_content += '<p>排期ID：' + str(ad.DE_campaign_id) + '  排期名：' + ad.name.encode('utf-8') + '</p>'
        html_content += '<ul>'
        for flight in staff_2notify_dict[staff][ad]:
            if flights_clicks_tracked.has_key( flight.DE_flight_id ):
                html_content += '<li>' + flight.media.c_name.encode('utf-8') + ' ' + flight.channel.c_name.encode('utf-8') + ' ' + flight.media_ad_info.adform.encode('utf-8') + ' ngAdID:' + str(flight.DE_ad_id) + '    clicks:' + str(flights_clicks_tracked[flight.DE_flight_id]) + '<br />'
                html_content += flight.DE_backend_url.encode('utf-8') + '</li>'
            else:
                html_content += '<li>' + flight.media.c_name.encode('utf-8') + ' ' + flight.channel.c_name.encode('utf-8') + ' ' + flight.media_ad_info.adform.encode('utf-8') + ' ngAdID:' + str(flight.DE_ad_id) + '    No clicks!<br />'
                html_content += flight.DE_backend_url.encode('utf-8') + '</li>'
        html_content += '</ul>'

        uploaders.add(ad.uploader.email)
        
    msg = EmailMessage('以下广告位今日无监测数据', html_content, 'andc-it@and-c.com', [staff.email]+list(uploaders), settings.CHECK_PLANNED_FLIGHT_CC) if lenovo_related == False else EmailMessage('以下广告位今日无监测数据', html_content, 'andc-it@and-c.com', [staff.email]+list(uploaders), settings.CHECK_PLANNED_FLIGHT_CC)
    msg.content_subtype = 'html'
    msg.send()


'''
print "Planned flights set:"
print planned_flights_set
print "Flights updated set:"
print flights_updated
print "Flights 2 notify:"
print flights_2notify
print "Ads 2 notify:"
print ads_2notify_dict
print "Ad related staff:"
print staff_2notify_dict
'''

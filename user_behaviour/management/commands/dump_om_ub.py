#encoding=utf8

import os
import csv
import datetime
import urllib2
from ftplib import FTP

from django.core.management.base import BaseCommand

from MediaChooser.user_behaviour.models import UserBehaviour
from MediaChooser.media_planning.models import Flight
from MediaChooser.ad.models import Ad

from googleanalytics import Connection

class Command(BaseCommand):

    def handle(self, *args, **options):        
        update_om()
        update_ga()
        #update_ga_campaign('35636139')

today = datetime.date.today()
#today = '20100522'
yesterday = today - datetime.timedelta(days=1)
#yesterday = datetime.date(2010,9,27)

def update_om():            
    filename = "Report%s.csv" % str(''.join(str(yesterday).split('-')))
    _get_file_from_ftp(filename)
    dir = os.path.abspath(os.path.split(__file__)[0])
    filename = os.path.join(dir,filename)
    reader = _reader_csv(filename)
    for row in reader:
        startdate, tracking_code, uv, visits, pv, products_view, cart_addition, \
            checkouts, orders, revenue = row
        if len(tracking_code)==5:
            try:
                flight = Flight.objects.get(DE_ad_id = tracking_code)
            except Flight.DoesNotExist:
                continue
                    
            try:
                ub = UserBehaviour.objects.get(tracking_code = tracking_code,startdate=date_trans(startdate), level='om')
                #ub.level ='om'
                #ub.save()
            except UserBehaviour.DoesNotExist:
                ub = UserBehaviour(startdate=date_trans(startdate),tracking_code= tracking_code,\
                    pv=int(pv),uv=int(uv),visits=int(visits),products_view=int(products_view), \
                    cart_addition=int(cart_addition), checkouts=int(checkouts), \
                    orders=int(orders), revenue=revenue, level="om")
                ub.save()
            

def update_ga():
    connection = Connection('zhaoxiaofan@and-c.com', 'xiaofan_andc')
    #live_ads = Ad.objects.filter(start_day__lte=yesterday, end_day__gte=yesterday).exclude(ga_pid='')
    live_ads = Ad.objects.filter(ga_pid='35636139')
    
    if list(live_ads) == []:
        print 'ga no ads'
        return 
    
    for ad in live_ads:
        account = connection.get_account(ad.ga_pid)
        
        try_times = 3
        i = 0
        
        while(i<try_times):
            try:
                data = account.get_data(yesterday, yesterday, metrics=['visits','pageviews','timeOnSite', 'bounces', 'entrances'], dimensions=['source'])
                break
            except:
                continue
        
        for d in data.list:
            tracking_code = d[0][0]
            visits = d[1][0]
            pageviews = d[1][1]
            timeOnsite = d[1][2]
            bounces = d[1][3]
            entrances = d[1][4]
            
            if len(tracking_code) == 5 and tracking_code.isdigit():
                try:
                    flight = Flight.objects.get(DE_ad_id = tracking_code)
                except Flight.DoesNotExist:
                    continue
                        
                try:
                    ub = UserBehaviour.objects.get(tracking_code = tracking_code,startdate=yesterday,level='ga')
                except UserBehaviour.DoesNotExist:
                    ub = UserBehaviour(startdate=yesterday,tracking_code= tracking_code,\
                        pv=pageviews, visits=visits,time_onsite=timeOnsite, bounces=int(bounces), entrances=int(entrances), level='ga')
                    ub.save()


def update_ga_campaign(ga_id):
    connection = Connection('zhaoxiaofan@and-c.com', 'xiaofan_andc')
    account = connection.get_account(ga_id)
    live_ad = Ad.objects.get(ga_pid=ga_id)
    
    days = (live_ad.end_day - live_ad.start_day).days
        
    for n in range(days):
        day = live_ad.start_day + datetime.timedelta(days=n)
        try_times = 3
        i = 0
        
        while(i<try_times):
            try:
                data = account.get_data(day, day, metrics=['visits','pageviews','timeOnSite', 'bounces', 'entrances'], dimensions=['source'])
                break
            except:
                continue
        
        for d in data.list:
            tracking_code = d[0][0]
            visits = d[1][0]
            pageviews = d[1][1]
            timeOnsite = d[1][2]
            bounces = d[1][3]
            entrances = d[1][4]
            
            if len(tracking_code) == 5 and tracking_code.isdigit():
                try:
                    flight = Flight.objects.get(DE_ad_id = tracking_code)
                except Flight.DoesNotExist:
                    continue
                        
                try:
                    ub = UserBehaviour.objects.get(tracking_code = tracking_code,startdate=day,level='ga')
                except UserBehaviour.DoesNotExist:
                    ub = UserBehaviour(startdate=day, tracking_code= tracking_code,\
                        pv=pageviews, visits=visits,time_onsite=timeOnsite, bounces=int(bounces), entrances=int(entrances), level='ga')
                    ub.save()
    
        

def _reader_csv(filename):
    reader = csv.reader(open(filename))
    return reader


def _get_file_from_ftp(filename):
    host = "211.94.190.82"
    username = "it"
    password = "it@ftp"

    remotepath = '/omniture'

    ftp = FTP(host)
    ftp.login(username, password)
    ftp.cwd(remotepath)
    dir = os.path.abspath(os.path.split(__file__)[0])
    filename = os.path.join(dir,filename)
    fd = open(filename, 'wb')
    ftp.retrbinary('RETR %s' % os.path.basename(filename),fd.write)
    fd.close()
    ftp.close()

def date_trans(date):
    parsed = datetime.datetime.strptime(date, '%B %d, %Y')
    converted = datetime.datetime(parsed.year, parsed.month, parsed.day)
    return converted

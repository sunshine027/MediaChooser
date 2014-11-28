#! /usr/bin/env python
#coding=utf-8

from MediaChooser.ad.models import Ad
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.mail import send_mass_mail
import sys
import pyodbc
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

# get mps that still not imported to MC within a period, email to related uploader.
# check out if there stored email info in DE database.

# make everydays click updating two times a day, offer mail notification if no clicks tracked.

someday_before = datetime.date.today()-datetime.timedelta(days=int(settings.MP_SEARCH_SPAN))

de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')
de_cursor = de_db.cursor()
sql = 'select a.id, b.email from admanager65.ng_insertionorders a, admanager65.ng_contacts b where a.creationdate > to_date(\'%s\', \'YYYY-MM-DD\') and a.createdbyuserid = b.linkuserid and a.status = 1' % someday_before

de_mp = set()
de_mp_dict = dict()
de_cursor.execute(sql)
for row in de_cursor:
    de_mp.add(row[0])
    de_mp_dict[row[0]] = row[1]
de_cursor.close()

mc_mp = set()
ads = Ad.objects.filter(create_time__gt=someday_before)
for ad in ads:
    mc_mp.add(ad.DE_campaign_id)

unuploaded_mp = de_mp.difference(mc_mp)
concerned_users = dict()
for mp in unuploaded_mp:
    if de_mp_dict[mp] is not None and concerned_users.has_key(de_mp_dict[mp]):
        concerned_users[de_mp_dict[mp]].append(mp)
    else:
        concerned_users[de_mp_dict[mp]] = [mp]


ldf_test = 'ludanfeng@and-c.com'

mail_data = []
for user in concerned_users:
    mail_data.append(('提醒：以下排期尚未录入MediaChooser！', ', '.join([str(x) for x in concerned_users[user]]), 'andc-it@and-c.com', [user]))

send_mass_mail(tuple(mail_data))

"""
print de_mp, de_mp_dict
for ad in ads:
    print ad.DE_campaign_id

print unuploaded_mp

print concerned_users
"""

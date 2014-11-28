#! /usr/bin/env python
#coding=utf-8

from django.core.management.base import BaseCommand
# from MediaChooser.media_planning.views import refresh_mp
from MediaChooser.ad.models import Ad
from MediaChooser.media_planning.models import Flight
from django.core.exceptions import ObjectDoesNotExist
import pyodbc

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')


# Got all mps uploaded.
for ad in Ad.objects.all():
    DE_campaign_id = ad.DE_campaign_id
    sql = 'select a.flightid, a.clickurl from admanager65.ng_ads a, admanager65.ng_flights b where a.flightid=b.id and b.orderid=%s' % DE_campaign_id
    de_cursor = de_db.cursor()
    de_cursor.execute(sql)
    for row in de_cursor:
        try:
            flight = Flight.objects.get(DE_flight_id = row[0])
            flight.clickurl = row[1]
            flight.save()
        except ObjectDoesNotExist:
            pass
        
    de_cursor.close()

# For every mp, retrieve every clickurl for related flight. Then update clickurl field.

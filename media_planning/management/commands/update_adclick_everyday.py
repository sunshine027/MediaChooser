from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from django.conf import settings
from MediaChooser.media_planning.models import Flight, DE_ClickData
from MediaChooser.media_planning.views import refresh_mp
from MediaChooser.ad.models import Ad
import pyodbc
import datetime

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')

yesterday = datetime.date.today()-datetime.timedelta(days=1)
de_clickdata_need2be_updated = DE_ClickData.objects.filter(date=datetime.date.today()-datetime.timedelta(days=1))
ad_need2be_updated = set()

sql = 'select flightid, sum(eventcount) from admanager65.ng_sum_fixed_h where startdate=to_date(\'%s\', \'YYYY-MM-DD\') and eventtype=4 group by flightid' % yesterday
de_cursor = de_db.cursor()
de_cursor.execute(sql)
for row in de_cursor:
    eventcount = int(row[1]*settings.CLICK_COMPENSATION_COEFFICIENT)
    try:
        flight = Flight.objects.get(DE_flight_id=row[0])
        if eventcount > settings.USEFUL_CLICK_NUMBER:
            ad_need2be_updated.add(flight.ad)
        try:
            clickdata = DE_ClickData.objects.get(flight=flight, date=yesterday)
            clickdata.eventtype = 4
            clickdata.eventcount = eventcount
            clickdata.save()
        except ObjectDoesNotExist:
            if eventcount > settings.USEFUL_CLICK_NUMBER:
                clickdata = DE_ClickData(ad=flight.ad, media=flight.media, channel=flight.channel, media_ad_info=flight.media_ad_info, flight=flight, date=yesterday, if_planned_spending=False, eventtype=4, eventcount=eventcount)
                clickdata.save()
    except ObjectDoesNotExist:
        print 'Flight not exist! flightid: ' + str(row[0])

de_cursor.close()

for ad in ad_need2be_updated:
    refresh_mp(ad.DE_campaign_id)

print 'Yesterdays update finished!'

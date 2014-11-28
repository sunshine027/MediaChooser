from django.core.management.base import BaseCommand
from MediaChooser.media_planning.models import Flight
import pyodbc

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')
for flight in Flight.objects.all():
    sql = 'select id from admanager65.ng_ads where flightid=%s' % (flight.DE_flight_id)
    de_cursor = de_db.cursor()
    de_cursor.execute(sql)
    for row in de_cursor:
        if row[0] is not None:
            flight.DE_ad_id = row[0]
    de_cursor.close()
    flight.save()

print 'It finished!'

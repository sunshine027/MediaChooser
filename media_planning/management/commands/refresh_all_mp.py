from django.core.management.base import BaseCommand
from MediaChooser.ad.models import Ad
from MediaChooser.media_planning.views import refresh_mp
import time

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

start_time = time.time()

for ad in Ad.objects.all():
    refresh_mp(ad.DE_campaign_id)

end_time = time.time()

print 'It finished!'
print 'It costs ' + str(end_time-start_time) + 's.'

    

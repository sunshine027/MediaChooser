from django.contrib import admin
from media_planning.models import Flight

class FlightAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ['DE_campaign_id']
    
admin.site.register(Flight, FlightAdmin)
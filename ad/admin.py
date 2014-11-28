from MediaChooser.ad.models import Ad, AdType, AdCreative

from django.contrib import admin

class AdTypeAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ['desc', 'c_name', 'e_name', 'advantage', 'disadvantage']

class AdAdmin (admin.ModelAdmin):
    list_display = ('name', 'client','start_day', 'end_day','DE_campaign_id')
    search_fields = ['name']

class AdCreativeAdmin (admin.ModelAdmin):
    list_display = ('ad', 'creative')

#class MediaAdInfoAdmin(admin.ModelAdmin):
 #   save_on_top = True
  #  search_fields = ['adsize', 'adformat']

admin.site.register(AdType, AdTypeAdmin)
admin.site.register(Ad, AdAdmin)
admin.site.register(AdCreative, AdCreativeAdmin)
#admin.site.register(MediaAdInfo, MediaAdInfoAdmin)

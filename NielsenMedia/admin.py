from django.contrib import admin

from MediaChooser.NielsenMedia.models import NielsenCategory, NielsenMedia, NielsenChannel, \
    NielsenTrafficData, Province, NielsenOverlap
    
class NielsenCategoryAdmin(admin.ModelAdmin):
    list_display = ('c_name', 'e_name','parent')

class NielsenMediaAdmin(admin.ModelAdmin):
    list_display = ('c_name','domain','main_category','sub_category')
    search_fields = ['c_name','domain']

class NielsenChannelAdmin(admin.ModelAdmin):
    list_display = ('c_name','domain','media','main_category','sub_category')
    search_fields = ['c_name','domain']

class NielsenTrafficDataAdmin(admin.ModelAdmin):
    list_display = ('media','media_domain','channel','channel_domain', 'province','sample_ub','sample_ub_freq','sample_ts','sample_ts','week')
    list_filter = ('province',)
    search_fields = ['media__c_name', 'media__domain', 'channel__c_name','channel__e_name']
    
    def media_domain(self, obj):
        return obj.media.domain
    
    
    def channel_domain(self, obj):
        return obj.channel.domain
    

class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('c_name','e_name')

class NielsenOverlapAdmin(admin.ModelAdmin):
    list_display = ('media_a','media_b','net_ub','ub_dup','dup')
    search_fields = ['media_a__c_name']
    list_filter = ('week',)
    
admin.site.register(NielsenCategory, NielsenCategoryAdmin)
admin.site.register(NielsenMedia, NielsenMediaAdmin)
admin.site.register(NielsenChannel, NielsenChannelAdmin)
admin.site.register(NielsenTrafficData, NielsenTrafficDataAdmin)
admin.site.register(Province, ProvinceAdmin)
admin.site.register(NielsenOverlap, NielsenOverlapAdmin)
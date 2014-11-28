from MediaChooser.media.models import MediaCategory, Media, MediaAttrForPR, MediaOverlapRatio, MediaOfflineRes, MediaOfflineRes, Channel

from django.contrib import admin

class MediaCategoryAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('c_name', 'parent', 'e_name')
    search_fields = ['c_name', 'e_name', 'e_abbr', 'desc']

class MediaAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('id', 'c_name', 'domain', 'e_name','first_category','second_category')
    search_fields = ['c_name', 'e_name', 'desc', 'zipcode', 'addr', 'advantage', 'issue_organization', 'domain']

class MediaAttrForPRAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ['level']

class MediaOverlapRatioAdmin(admin.ModelAdmin):
    save_on_top = True

class MediaOfflineResAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ['res_type', 'advantage']

class ChannelAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ['c_name', 'weight']

admin.site.register(MediaCategory, MediaCategoryAdmin)
admin.site.register(Media, MediaAdmin)
admin.site.register(MediaAttrForPR, MediaAttrForPRAdmin)
admin.site.register(MediaOverlapRatio, MediaOverlapRatioAdmin)
admin.site.register(MediaOfflineRes, MediaOfflineResAdmin)
admin.site.register(Channel, ChannelAdmin)

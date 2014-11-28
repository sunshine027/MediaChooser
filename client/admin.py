from MediaChooser.client.models import Client, DomainName

from django.contrib import admin

class ClientAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ['c_name', 'e_name', 'desc']
    list_display = ('c_name', 'e_name', 'industry')

admin.site.register(Client, ClientAdmin)
admin.site.register(DomainName)
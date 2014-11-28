from MediaChooser.user_behaviour.models import UserBehaviour

from django.contrib import admin

class UserBehaviourAdmin(admin.ModelAdmin):
    save_on_top = True
    list_display = ('startdate', 'tracking_code', 'pv','uv','visits','products_view','cart_addition','checkouts','orders','revenue')

admin.site.register(UserBehaviour, UserBehaviourAdmin)

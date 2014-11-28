from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
# Example:
# (r'^demo/', include('demo.foo.urls')),

# Uncomment the admin/doc line below and add 'django.contrib.admindocs'
# to INSTALLED_APPS to enable admin documentation:
# (r'^admin/doc/', include('django.contrib.admindocs.urls')),

#url(r'^$', 'MediaChooser.ad_resource_mgmt.views.query', name="query"),
# Uncomment the next line to enable the admin:
(r'^', include('ad_resource_mgmt.urls')),
(r'^admin/(.*)', admin.site.root),
(r'^accounts/', include('registration.urls')),
(r'^weekly-report/', include('media_weekly_report.urls')),

(r'^client/', include('client.urls')),
(r'^media-planning/', include('media_planning.urls')),
(r'^media/', include('media.urls')),
(r'^pr/', include('pr.urls')),
#(r'^nielsen-media/', include('NielsenMedia.urls')),
#(r'^torres/', include('torres.urls')),

)

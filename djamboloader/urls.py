from django.conf.urls import *

urlpatterns = patterns('',
    url(r'^(?P<library>(\w+|))/?combo$', 'djamboloader.views.load', name='load'),
)

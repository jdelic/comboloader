from django.conf.urls import patterns, include, url
from jscombo.views import HealthCheck, load

urlpatterns = patterns('',
    url(r'^combo$', load, name='load'),
    url(r'^health$', HealthCheck.as_view(), name='health'),
)

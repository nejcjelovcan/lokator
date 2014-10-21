from django.conf.urls import patterns, include, url
from django.contrib import admin
from visits.views import IndexView, logoutView

urlpatterns = patterns('',
    url('^$', IndexView.as_view(), name='index'),
    url(r'^logout/', logoutView, name='logout'),
    url('', include('social.apps.django_app.urls', namespace='social')),
)

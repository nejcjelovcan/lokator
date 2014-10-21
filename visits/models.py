import pytz
from datetime import datetime, timedelta

from django.db import models
from django.conf import settings
from django.contrib.gis.db import models as gismodels
from django.contrib.sessions.models import Session
from django.contrib.sessions.backends.db import SessionStore
from django.contrib.auth.models import User
from django.contrib.gis.geos import Point

import GeoIP
import geocoder
gip = GeoIP.open(settings.GEOIP_DB or "GeoLiteCity.dat", GeoIP.GEOIP_STANDARD)
def get_location_by_ip(ip):
    location = None
    loc = geocoder.ip(ip)
    if loc and loc.ok:
        location, created = Location.objects.get_or_create(location=Point(loc.lng, loc.lat), defaults={'address': loc.address})
    else:
        record = gip.record_by_addr(ip)
        if record:
            location, created = Location.objects.get_or_create(location=Point(record.get('longitude'), record.get('latitude')), defaults={
                'address': '%s, %s'%(record.get('city'), record.get('country_name')) if record.get('city') else record.get('country_name')
            })
    return location

class LocationManager(gismodels.GeoManager):
    def filterActiveVisitorsLocations(self, referencePoint):
        locations = Visit.objects.filterActiveVisitors().order_by('session_key').distinct('session_key').values_list('location', flat=True)
        locations = Location.objects.filter(id__in=locations)
        if referencePoint:
            locations = locations.distance(referencePoint).order_by('distance')
        return locations

class Location(gismodels.Model):
    location = gismodels.PointField()
    address = gismodels.TextField()

    objects = LocationManager()

    def __unicode__(self):
        return self.address

ACTIVE_EXPIRE = 60

class VisitManager(models.Manager):

    def filterActiveVisitors(self):
        return Visit.objects.filter(time__gte=datetime.now()-timedelta(seconds=ACTIVE_EXPIRE)).exclude(session_key=None)

    def countActiveVisitors(self):
        return self.filterActiveVisitors().order_by('session_key').distinct('session_key').count()

    def filterDayVisits(self):
        return Visit.objects.order_by('session_key', '-time').distinct('session_key').exclude(session_key=None).filter(time__gte=datetime.now()-timedelta(1))

    def getOrderedDayVisits(self):
        visits = list(self.filterDayVisits())
        visits.sort(key=lambda x: -int(x.time.strftime('%s')))
        return visits

class Visit(models.Model):
    time = models.DateTimeField(auto_now_add=True)
    ip = models.CharField(max_length=255)
    session_key = models.CharField(max_length=255, null=True)
    user = models.ForeignKey(User, null=True)
    location = models.ForeignKey(Location, null=True)

    objects = VisitManager()

    def updateLocation(self):
        if not self.location:
            location = get_location_by_ip(self.ip)
            if location:
                location.save()
                self.location = location

    def isActive(self):
        now = datetime.utcnow()
        now = now.replace(tzinfo=pytz.utc)
        return now - self.time < timedelta(seconds=ACTIVE_EXPIRE)

    def __unicode__(self):
        return '[%s] %s'%(self.time.isoformat(), unicode(self.ip))

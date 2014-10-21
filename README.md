# lokator

Web service with map showing all visitors' locations (django, postgis, twitter login, foundation, leaflet)

## Installation

```
pip install -r requirements.txt
```

## Database

postgresql with postgis is needed


## Settings

Create lokator/settings_local.py and add

```
SOCIAL_AUTH_TWITTER_KEY = ''
SOCIAL_AUTH_TWITTER_SECRET = ''
DATABASES = {
  'default': {
    'NAME': '',
    'HOST': 'localhost',
    'PORT': 5432,
    'USER': '',
    'PASSWORD': '',
    'ENGINE': 'django.contrib.gis.db.backends.postgis',
    'OPTIONS': { 'autocommit': True, }
  }
}
GEOIP_DB = 'GeoLiteCity.dat'
```

## Django

```
./manage.py syncdb
./manage.py collectstatic
```

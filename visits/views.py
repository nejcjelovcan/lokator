import json
from datetime import datetime

from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.generic import TemplateView
from django.template.loader import get_template
from django.template import Context
from django.contrib.auth import logout
from django.contrib.humanize.templatetags.humanize import naturaltime

from visits.models import Visit, Location, ACTIVE_EXPIRE

def logoutView(request):
    logout(request)
    return redirect('index')

class IndexView(TemplateView):
    template_name = 'index.html'

    def get_client_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        ip = None
        if x_forwarded_for:
            try:
                ip = filter(lambda x: x != 'unknown', map(str.strip, x_forwarded_for.split(',')))[0]
            except IndexError: pass
        else:
            ip = self.request.META.get('REMOTE_ADDR')
        if ip == '127.0.0.1': ip = '194.249.198.48' # @TODO @DEBUG
        return ip

    def record_visit(self):
        user = None if self.request.user.is_anonymous() else self.request.user
        visit = Visit(session_key=self.request.session.session_key, user=user, ip=self.get_client_ip())
        visit.updateLocation()
        visit.save()

    def render_welcome_text(self, add=0):
        visitors = Visit.objects.countActiveVisitors()+add
        return 'There are currently %s users on site - including you!'%visitors

    def format_visit_time(self, visit):
        return naturaltime(datetime.now() if visit.isActive() else visit.time)

    def render_day_visits(self, visits=None):
        if not visits: visits = Visit.objects.getOrderedDayVisits()
        return get_template('_day_visits.html').render(
            Context({
                'visits':[dict(\
                    time = self.format_visit_time(visit),\
                    address = visit.location.address if visit.location else 'unknown',\
                    username = visit.user.username if visit.user else 'anonymous'\
                ) for visit in visits]
            })
        )

    def render_current_visitor_locations(self, locations=None):
        if not locations: locations = Location.objects.filterActiveVisitorsLocations(self.get_current_location())
        return '\n'.join(['<div>%s</div>'%location.address for location in locations])

    def get_current_location(self):
        location = None
        try:
            location = Visit.objects.filter(session_key=self.request.session.session_key).order_by('-time')[0].location
            if location: location = location.location
        except IndexError: pass
        return location

    def get_context_data(self, **kwargs):
        context = super(IndexView, self).get_context_data(**kwargs)
        if self.request.user.is_anonymous():
            context['subheader'] = self.render_welcome_text(0 if self.request.session.session_key else 1)
        else:
            context['visitorLocations'] = self.render_current_visitor_locations()
            context['dayVisits'] = self.render_day_visits()
            context['points'] = [[visit.location.location.y, visit.location.location.x, visit.isActive()] for visit in Visit.objects.filterDayVisits()]

        return context

    def get(self, request):
        if not request.session.session_key:
            request.session.set_test_cookie()

        self.record_visit()

        if request.is_ajax():
            ctx = self.get_context_data()
            return HttpResponse(json.dumps(dict([pair for pair in ctx.items() if pair[0] != 'view'])), content_type='application/json')

        return super(IndexView, self).get(request)

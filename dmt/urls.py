from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from dmt.main.models import (
    Project, Milestone, Item, User, Client,
    Node)
from dmt.main.views import SearchView

admin.autodiscover()

redirect_after_logout = getattr(settings, 'LOGOUT_REDIRECT_URL', None)
auth_urls = (r'^accounts/', include('django.contrib.auth.urls'))
logout_page = (
    r'^accounts/logout/$',
    'django.contrib.auth.views.logout',
    {'next_page': redirect_after_logout})
if hasattr(settings, 'WIND_BASE'):
    auth_urls = (r'^accounts/', include('djangowind.urls'))
    logout_page = (
        r'^accounts/logout/$',
        'djangowind.views.logout',
        {'next_page': redirect_after_logout})

urlpatterns = patterns(
    '',
    auth_urls,
    logout_page,
    (r'^$', TemplateView.as_view(template_name="main/index.html")),
    (r'^admin/', include(admin.site.urls)),
    (r'^api/1.0/', include('dmt.api.urls')),
    (r'^claim/', include('dmt.claim.urls')),
    (r'^search/$', SearchView.as_view()),
    (r'^client/$', ListView.as_view(model=Client, paginate_by=100)),
    (r'^client/(?P<pk>\d+)/$', DetailView.as_view(model=Client)),
    (r'^forum/$', ListView.as_view(model=Node, paginate_by=20)),
    (r'^forum/(?P<pk>\d+)/$', DetailView.as_view(model=Node)),
    (r'^item/(?P<pk>\d+)/$', DetailView.as_view(model=Item)),
    (r'^milestone/(?P<pk>\d+)/$', DetailView.as_view(model=Milestone)),
    (r'^project/$', ListView.as_view(model=Project)),
    (r'^project/(?P<pk>\d+)/$', DetailView.as_view(model=Project)),
    (r'^report/', include('dmt.report.urls')),
    (r'^user/$', ListView.as_view(model=User)),
    (r'^user/(?P<pk>\w+)/$', DetailView.as_view(model=User)),
    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'^smoketest/', include('smoketest.urls')),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

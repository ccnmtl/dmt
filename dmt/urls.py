from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from rest_framework import routers
from django_filters.views import FilterView
from dmt.main.models import (
    Project, Milestone, Item, User, Client,
    Node)
from dmt.main.views import (
    SearchView, UserViewSet, ClientViewSet, ProjectViewSet,
    MilestoneViewSet, ItemViewSet, ProjectMilestoneList,
    MilestoneItemList, AddCommentView, ResolveItemView)
from dmt.main.feeds import ForumFeed

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'milestones', MilestoneViewSet)
router.register(r'items', ItemViewSet)

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
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^drf/projects/(?P<pk>\d+)/milestones/$',
        ProjectMilestoneList.as_view(), name='project-milestones'),
    url(r'^drf/milestones/(?P<pk>\d+)/items/$',
        MilestoneItemList.as_view(), name='milestone-items'),
    (r'^drf/', include(router.urls)),
    (r'^claim/', include('dmt.claim.urls')),
    (r'^search/$', SearchView.as_view()),
    (r'^client/$', FilterView.as_view(model=Client, paginate_by=100)),
    (r'^client/(?P<pk>\d+)/$', DetailView.as_view(model=Client)),
    (r'^forum/$', ListView.as_view(model=Node, paginate_by=20)),
    (r'^forum/(?P<pk>\d+)/$', DetailView.as_view(model=Node)),
    (r'^item/(?P<pk>\d+)/$', DetailView.as_view(model=Item)),
    (r'^item/(?P<pk>\d+)/comment/$', AddCommentView.as_view()),
    (r'^item/(?P<pk>\d+)/resolve/$', ResolveItemView.as_view()),
    (r'^milestone/(?P<pk>\d+)/$', DetailView.as_view(model=Milestone)),
    (r'^project/$', FilterView.as_view(model=Project)),
    (r'^project/(?P<pk>\d+)/$', DetailView.as_view(model=Project)),
    (r'^report/', include('dmt.report.urls')),
    (r'^user/$', FilterView.as_view(model=User)),
    (r'^user/(?P<pk>\w+)/$', DetailView.as_view(model=User)),
    (r'^feeds/forum/rss/$', ForumFeed()),
    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'^smoketest/', include('smoketest.urls')),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

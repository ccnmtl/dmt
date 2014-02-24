from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from rest_framework import routers
from dmt.main.views import (
    SearchView, UserViewSet, ClientViewSet, ProjectViewSet,
    MilestoneViewSet, ItemViewSet, ProjectMilestoneList,
    MilestoneItemList, AddCommentView, ResolveItemView,
    InProgressItemView, VerifyItemView, ReopenItemView,
    SplitItemView, ItemDetailView, IndexView, ClientListView,
    ClientDetailView, ForumView, NodeDetailView, MilestoneDetailView,
    ProjectListView, ProjectDetailView, UserListView,
    UserDetailView, NodeReplyView, ProjectAddTodoView)
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
    (r'^$', IndexView.as_view()),
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
    (r'^client/$', ClientListView.as_view()),
    (r'^client/(?P<pk>\d+)/$', ClientDetailView.as_view()),
    (r'^forum/$', ForumView.as_view()),
    (r'^forum/(?P<pk>\d+)/$', NodeDetailView.as_view()),
    (r'^forum/(?P<pk>\d+)/reply/$', NodeReplyView.as_view()),
    (r'^item/(?P<pk>\d+)/$', ItemDetailView.as_view()),
    (r'^item/(?P<pk>\d+)/comment/$', AddCommentView.as_view()),
    (r'^item/(?P<pk>\d+)/resolve/$', ResolveItemView.as_view()),
    (r'^item/(?P<pk>\d+)/inprogress/$', InProgressItemView.as_view()),
    (r'^item/(?P<pk>\d+)/verify/$', VerifyItemView.as_view()),
    (r'^item/(?P<pk>\d+)/reopen/$', ReopenItemView.as_view()),
    (r'^item/(?P<pk>\d+)/split/$', SplitItemView.as_view()),
    (r'^milestone/(?P<pk>\d+)/$', MilestoneDetailView.as_view()),
    (r'^project/$', ProjectListView.as_view()),
    (r'^project/(?P<pk>\d+)/$', ProjectDetailView.as_view()),
    (r'^project/(?P<pk>\d+)/add_todo/$', ProjectAddTodoView.as_view()),
    (r'^report/', include('dmt.report.urls')),
    (r'^user/$', UserListView.as_view()),
    (r'^user/(?P<pk>\w+)/$', UserDetailView.as_view()),
    (r'^feeds/forum/rss/$', ForumFeed()),
    url(r'^_impersonate/', include('impersonate.urls')),
    (r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    (r'^smoketest/', include('smoketest.urls')),
    (r'^uploads/(?P<path>.*)$',
     'django.views.static.serve', {'document_root': settings.MEDIA_ROOT}),
)

from django.conf.urls import include, patterns, url

from rest_framework import routers

from .views import (
    AddTrackerView,
    ItemHoursView, GitUpdateView,
    UserViewSet, ProjectMilestoneList,
    ClientViewSet, ProjectViewSet,
    MilestoneViewSet, ItemViewSet,
    MilestoneItemList, NotifyView
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'milestones', MilestoneViewSet)
router.register(r'items', ItemViewSet)

urlpatterns = patterns(
    '',
    (r'^', include(router.urls)),
    url(r'^notify/(?P<pk>\d+)/$', NotifyView.as_view(), name='notify'),
    url(r'^api-auth/',
        include('rest_framework.urls', namespace='rest_framework')),
    url(r'^projects/(?P<pk>\d+)/milestones/$',
        ProjectMilestoneList.as_view(), name='project-milestones'),
    url(r'^milestones/(?P<pk>\d+)/items/$',
        MilestoneItemList.as_view(), name='milestone-items'),
    (r'^trackers/add/', AddTrackerView.as_view()),
    (r'^items/(?P<pk>\d+)/hours/$', ItemHoursView.as_view()),
    (r'^git/$', GitUpdateView.as_view()),
)

from django.urls import include, re_path

from rest_framework import routers

from dmt.api.views import (
    AddTrackerView,
    ItemHoursView, GitUpdateView,
    UserViewSet, ProjectMilestoneList,
    ClientViewSet, ProjectViewSet,
    MilestoneViewSet, ItemViewSet,
    MilestoneItemList, NotifyView,
    ExternalAddItemView, JiraExternalAddItemView
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'milestones', MilestoneViewSet)
router.register(r'items', ItemViewSet)

urlpatterns = [
    re_path(r'^', include(router.urls)),
    re_path(r'^notify/(?P<pk>\d+)/$', NotifyView.as_view(), name='notify'),
    re_path(r'^api-auth/', include('rest_framework.urls',
                                   namespace='rest_framework')),
    re_path(r'^projects/(?P<pk>\d+)/milestones/$',
            ProjectMilestoneList.as_view(), name='project-milestones'),
    re_path(r'^milestones/(?P<pk>\d+)/items/$',
            MilestoneItemList.as_view(), name='milestone-items'),
    re_path(r'^trackers/add/', AddTrackerView.as_view(), name='add-tracker'),
    re_path(r'^items/(?P<pk>\d+)/hours/$', ItemHoursView.as_view(),
            name='item-hours'),
    re_path(r'^git/$', GitUpdateView.as_view(), name='git-update'),
    re_path(r'^external_add_item/$', ExternalAddItemView.as_view(),
            name='external-add-item'),
    re_path(r'^jira_add_item/$', JiraExternalAddItemView.as_view(),
            name='jira-add-item'),
]

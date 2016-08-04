from django.conf.urls import include, url

from rest_framework import routers

from dmt.api.views import (
    AddTrackerView,
    ItemHoursView, GitUpdateView,
    UserViewSet, ProjectMilestoneList,
    ClientViewSet, ProjectViewSet,
    MilestoneViewSet, ItemViewSet,
    MilestoneItemList, NotifyView,
    ExternalAddItemView
)

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'clients', ClientViewSet)
router.register(r'projects', ProjectViewSet)
router.register(r'milestones', MilestoneViewSet)
router.register(r'items', ItemViewSet)

urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^notify/(?P<pk>\d+)/$', NotifyView.as_view(), name='notify'),
    url(r'^api-auth/', include('rest_framework.urls',
                               namespace='rest_framework')),
    url(r'^projects/(?P<pk>\d+)/milestones/$',
        ProjectMilestoneList.as_view(), name='project-milestones'),
    url(r'^milestones/(?P<pk>\d+)/items/$',
        MilestoneItemList.as_view(), name='milestone-items'),
    url(r'^trackers/add/', AddTrackerView.as_view(), name='add-tracker'),
    url(r'^items/(?P<pk>\d+)/hours/$', ItemHoursView.as_view(),
        name='item-hours'),
    url(r'^git/$', GitUpdateView.as_view(), name='git-update'),
    url(r'^external_add_item/$', ExternalAddItemView.as_view(),
        name='external-add-item'),
]

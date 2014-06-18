from django.conf.urls import patterns
from .views import (
    AllProjectsView, AutocompleteProjectView, AddTrackerView,
    ItemHoursView, GitUpdateView)


urlpatterns = patterns(
    '',
    (r'^projects/all/', AllProjectsView.as_view()),
    (r'^projects/autocomplete/', AutocompleteProjectView.as_view()),
    (r'^trackers/add/', AddTrackerView.as_view()),
    (r'^items/(?P<pk>\d+)/hours/$', ItemHoursView.as_view()),
    (r'^git/$', GitUpdateView.as_view()),
)

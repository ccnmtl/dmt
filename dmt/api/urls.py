from django.conf.urls.defaults import patterns
from .views import AllProjectsView, AutocompleteProjectView, AddTrackerView


urlpatterns = patterns(
    '',
    (r'^projects/all/', AllProjectsView.as_view()),
    (r'^projects/autocomplete/', AutocompleteProjectView.as_view()),
    (r'^trackers/add/', AddTrackerView.as_view()),
)

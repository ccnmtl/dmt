from django.conf.urls import patterns
from django.views.generic import TemplateView


urlpatterns = patterns(
    '',
    (r'^$', TemplateView.as_view(template_name="report/report_list.html")),
)

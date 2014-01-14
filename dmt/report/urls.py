from django.conf.urls import patterns
from django.views.generic import TemplateView
import dmt.report.views as views


urlpatterns = patterns(
    '',
    (r'^$', TemplateView.as_view(template_name="report/report_list.html")),
    (r'^user/(?P<pk>\w+)/weekly/$', views.UserWeeklyView.as_view()),
    (r'^staff/$', views.StaffReportView.as_view()),
)

from django.conf.urls import patterns, url
from django.views.generic import TemplateView
import dmt.report.views as views


urlpatterns = patterns(
    '',
    url(r'^$', TemplateView.as_view(template_name="report/report_list.html"),
        name='report_list'),
    url(r'^user/(?P<pk>\w+)/weekly/$', views.UserWeeklyView.as_view(),
        name='weekly_report'),
    url(r'^user/(?P<pk>\w+)/yearly/$', views.UserYearlyView.as_view(),
        name='yearly_report'),
    url(r'^yearly_review/$', views.YearlyReviewView.as_view(),
        name='yearly_review'),
    url(r'^staff/$', views.StaffReportView.as_view(),
        name='staff_report'),
    (r'^staff/previous/$', views.StaffReportPreviousWeekView.as_view()),
)

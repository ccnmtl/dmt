from django.conf.urls import url
from django.views.generic import TemplateView
import dmt.report.views as views


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name="report/report_list.html"),
        name='report_list'),

    url(r'^active_projects/$', views.ActiveProjectsView.as_view(),
        name='active_projects_report'),
    url(r'^active_projects/export\w{0,50}$',
        views.ActiveProjectsExportView.as_view(),
        name='active_projects_report_export'),

    url(r'^project/(?P<pk>\d+)/hours/$', views.ProjectHoursView.as_view(),
        name='project-hours-report'),

    url(r'^user/(?P<pk>\w+)/weekly/$', views.UserWeeklyView.as_view(),
        name='user_weekly_report'),
    url(r'^user/(?P<pk>\w+)/yearly/$', views.UserYearlyView.as_view(),
        name='user_yearly_report'),
    url(r'^yearly_review/$', views.YearlyReviewView.as_view(),
        name='yearly_review_report'),

    url(r'^staff/$', views.StaffReportView.as_view(),
        name='staff_report'),
    url(r'^staff/export\w{0,50}$', views.StaffReportExportView.as_view(),
        name='staff_report_export'),

    url(r'^staff/previous/$', views.StaffReportPreviousWeekView.as_view()),

    url(r'^resolved/$', views.ResolvedView.as_view(),
        name='resolved_items_report'),
    url(r'^inprogress/$', views.InprogressView.as_view(),
        name='inprogress_items_report'),
    url(r'^passed_milestones/$', views.PassedMilestonesView.as_view(),
        name='passed_milestones_report'),
]

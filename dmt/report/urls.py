from django.urls import re_path
from django.views.generic import TemplateView
import dmt.report.views as views


urlpatterns = [
    re_path(
        r'^$', TemplateView.as_view(template_name="report/report_list.html"),
        name='report_list'),

    re_path(r'^active_projects/$', views.ActiveProjectsView.as_view(),
            name='active_projects_report'),
    re_path(r'^active_projects/export\w{0,50}$',
            views.ActiveProjectsExportView.as_view(),
            name='active_projects_report_export'),

    re_path(r'^project/(?P<pk>\d+)/hours/$', views.ProjectHoursView.as_view(),
            name='project-hours-report'),

    re_path(r'^user/(?P<pk>\w+)/weekly/$', views.UserWeeklyView.as_view(),
            name='user_weekly_report'),
    re_path(r'^user/(?P<pk>\w+)/yearly/$', views.UserYearlyView.as_view(),
            name='user_yearly_report'),
    re_path(r'^yearly_review/$', views.YearlyReviewView.as_view(),
            name='yearly_review_report'),

    re_path(r'^staff/$', views.StaffReportView.as_view(),
            name='staff_report'),
    re_path(r'^staff/export\w{0,50}$', views.StaffReportExportView.as_view(),
            name='staff_report_export'),

    re_path(r'^staff/previous/$', views.StaffReportPreviousWeekView.as_view()),

    re_path(r'^resolved/$', views.ResolvedView.as_view(),
            name='resolved_items_report'),
    re_path(r'^inprogress/$', views.InprogressView.as_view(),
            name='inprogress_items_report'),
    re_path(r'^passed_milestones/$', views.PassedMilestonesView.as_view(),
            name='passed_milestones_report'),

    re_path(r'^time_spent_by_user/$', views.TimeSpentByUser.as_view(),
            name='time_spent_by_user_report'),
    re_path(r'^time_spent_by_project/$', views.TimeSpentByProject.as_view(),
            name='time_spent_by_project_report'),
    re_path(r'^project_status/$', views.ProjectStatus.as_view(),
            name='project_status_report'),

    re_path(r'^capacity/$', views.StaffCapacityView.as_view(),
            name='staff_capacity'),
    re_path(
        r'^staff/capacity\w{0,50}$', views.StaffCapacityExportView.as_view(),
        name='staff_capacity_export'),


]

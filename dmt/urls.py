import django.views.static
from django.urls import path
from django.conf.urls import include, url
from django.contrib import admin
from django.conf import settings
from django.views.generic import TemplateView
from django_cas_ng import views as cas_views


from dmt.main.views import (
    AddTrackersView, SearchView,
    ActualTimeDeleteView,
    AddCommentView, CommentUpdateView, CommentDeleteView, ResolveItemView,
    InProgressItemView, VerifyItemView, ReopenItemView,
    SplitItemView, ItemDetailView,
    IndexView, ClientListView, AddClientView,
    ClientDetailView, ForumView, GroupDetailView, GroupListView,
    NodeDetailView, MilestoneDetailView,
    ProjectListView, MyProjectListView, ProjectDetailView,
    ProjectTimeLineView, ProjectTagListView, ProjectTagView,
    UserTimeLineView,
    UserListView, UserDetailView, NodeReplyView, ProjectAddTodoView,
    ProjectAddNodeView, TagItemView, RemoveTagFromItemView,
    TagNodeView, RemoveTagFromNodeView, DeleteTagView,
    TagDetailView, TagListView, ItemPriorityView, ReassignItemView,
    ChangeOwnerItemView, ProjectAddStatusUpdateView,
    StatusUpdateListView, StatusUpdateUpdateView, StatusUpdateDeleteView,
    NodeUpdateView, NodeDeleteView, UserUpdateView,
    ProjectCreateView, ProjectUpdateView, MilestoneUpdateView,
    ItemCreateView, BugCreateView, ItemUpdateView,
    ProjectAddItemView, DashboardView, MilestoneListView,
    ProjectRemoveUserView, ProjectAddPersonnelView, ProjectAddMilestoneView,
    ItemDeleteView, SignS3View, ItemAddAttachmentView,
    DeleteAttachmentView, GroupCreateView,
    DeactivateUserView, ItemMoveProjectView, RemoveUserFromGroupView,
    AddUserToGroupView, MilestoneDeleteView, OwnedItemsView,
    ItemSetMilestoneView, MergeTagView, ItemAddSubscriberView,
    ProjectPinView,
)
from dmt.main.feeds import ForumFeed, StatusUpdateFeed, ProjectFeed


urlpatterns = [
    url(r'^accounts/', include('django.contrib.auth.urls')),
    path('cas/login', cas_views.LoginView.as_view(),
         name='cas_ng_login'),
    path('cas/logout', cas_views.LogoutView.as_view(),
         name='cas_ng_logout'),
    url(r'^$', IndexView.as_view()),
    url(r'^admin/', admin.site.urls),
    url(r'^add_trackers/$', AddTrackersView.as_view(), name='add_trackers'),
    url(r'^api/1.0/', include('dmt.api.urls')),
    url(r'^actualtime/(?P<uuid>[^/]+)/delete/$',
        ActualTimeDeleteView.as_view(),
        name='delete_time'),
    url(r'^drf/', include('dmt.api.urls')),
    url(r'^oauth2/', include('oauth2_provider.urls', namespace='oauth2')),
    url(r'^search/$', SearchView.as_view()),
    url(r'^client/$', ClientListView.as_view()),
    url(r'^client/(?P<pk>\d+)/$', ClientDetailView.as_view(),
        name="client_detail"),
    url(r'^client/add/$', AddClientView.as_view(), name='add_client'),
    url(r'^sign_s3/$', SignS3View.as_view()),
    url(r'^forum/$', ForumView.as_view(), name='forum_list'),
    url(r'^forum/(?P<pk>\d+)/$', NodeDetailView.as_view()),
    url(r'^forum/(?P<pk>\d+)/reply/$', NodeReplyView.as_view()),
    url(r'^forum/(?P<pk>\d+)/tag/$', TagNodeView.as_view()),
    url(r'^forum/(?P<pk>\d+)/remove_tag/(?P<slug>[^/]+)/$',
        RemoveTagFromNodeView.as_view()),
    url(r'^forum/(?P<pk>\d+)/edit/$', NodeUpdateView.as_view()),
    url(r'^forum/(?P<pk>\d+)/delete/$', NodeDeleteView.as_view()),
    url(r'^group/create/$', GroupCreateView.as_view(), name='group_create'),
    url(r'^group/$', GroupListView.as_view(), name='group_list'),
    url(r'^group/(?P<pk>\w+)/$', GroupDetailView.as_view(),
        name='group_detail'),
    url(r'^group/(?P<pk>\w+)/remove_user/$', RemoveUserFromGroupView.as_view(),
        name='remove_user_from_group'),
    url(r'^group/(?P<pk>\w+)/add_user/$', AddUserToGroupView.as_view(),
        name='add_user_to_group'),
    url(r'^item/create/$', ItemCreateView.as_view(), name='item_create'),
    url(r'^bug/create/$', BugCreateView.as_view(), name='bug_create'),
    url(r'^item/(?P<pk>\d+)/$', ItemDetailView.as_view(), name='item_detail'),
    url(r'^item/(?P<pk>\d+)/edit/$', ItemUpdateView.as_view(),
        name='item_update'),
    url(r'^item/(?P<pk>\d+)/move_project/$', ItemMoveProjectView.as_view(),
        name='item-move-project'),
    url(r'^item/(?P<pk>\d+)/comment/$', AddCommentView.as_view()),
    url(r'^comment/(?P<pk>\d+)/update/$', CommentUpdateView.as_view(),
        name='comment_update'),
    url(r'^comment/(?P<pk>\d+)/delete/$', CommentDeleteView.as_view(),
        name='comment_delete'),
    url(r'^item/(?P<pk>\d+)/resolve/$', ResolveItemView.as_view()),
    url(r'^item/(?P<pk>\d+)/inprogress/$', InProgressItemView.as_view()),
    url(r'^item/(?P<pk>\d+)/verify/$', VerifyItemView.as_view()),
    url(r'^item/(?P<pk>\d+)/reopen/$', ReopenItemView.as_view()),
    url(r'^item/(?P<pk>\d+)/split/$', SplitItemView.as_view()),
    url(r'^item/(?P<pk>\d+)/tag/$', TagItemView.as_view()),
    url(r'^item/(?P<pk>\d+)/set_milestone/$',
        ItemSetMilestoneView.as_view(), name='set_item_milestone'),
    url(r'^item/(?P<pk>\d+)/remove_tag/(?P<slug>[^/]+)/$',
        RemoveTagFromItemView.as_view()),
    url(r'^item/(?P<pk>\d+)/priority/(?P<priority>\d)/$',
        ItemPriorityView.as_view()),
    url(r'^item/(?P<pk>\d+)/assigned_to/$', ReassignItemView.as_view()),
    url(r'^item/(?P<pk>\d+)/owner/$', ChangeOwnerItemView.as_view()),
    url(r'^item/(?P<pk>\d+)/delete/$', ItemDeleteView.as_view()),
    url(r'^item/(?P<pk>\d+)/add_attachment/$',
        ItemAddAttachmentView.as_view()),
    url(r'^attachment/(?P<pk>\d+)/delete/$', DeleteAttachmentView.as_view(),
        name="delete_attachment"),
    url(r'^item/(?P<pk>\d+)/add_subscriber/$',
        ItemAddSubscriberView.as_view(),
        name='add_subscriber'),
    url(r'^milestone/$', MilestoneListView.as_view()),
    url(r'^milestone/(?P<pk>\d+)/$', MilestoneDetailView.as_view(),
        name='milestone_detail'),
    url(r'^milestone/(?P<pk>\d+)/edit/$', MilestoneUpdateView.as_view()),
    url(r'^milestone/(?P<pk>\d+)/delete/$', MilestoneDeleteView.as_view(),
        name="delete_milestone"),
    url(r'^project/$', ProjectListView.as_view(), name='project_list'),
    url(r'^my_projects/$', MyProjectListView.as_view(),
        name='my_project_list'),
    url(r'^project/create/$', ProjectCreateView.as_view(),
        name='project_create'),
    url(r'^project/(?P<pk>\d+)/$', ProjectDetailView.as_view(),
        name='project_detail'),
    url(r'^project/(?P<pk>\d+)/pin/$', ProjectPinView.as_view(),
        name='project-pin'),
    url(r'^project/(?P<pk>\d+)/board/$', ProjectDetailView.as_view(
        template_name="main/project_board.html"),
        name='project_board'),
    url(r'^project/(?P<pk>\d+)/kanban/$', ProjectDetailView.as_view(
        template_name="main/project_kanban.html"),
        name='project_kanban'),
    url(r'^project/(?P<pk>\d+)/timeline/$', ProjectTimeLineView.as_view(),
        name='project_timeline'),
    url(r'^project/(?P<pk>\d+)/add_bug/$',
        ProjectAddItemView.as_view(item_type='bug')),
    url(r'^project/(?P<pk>\d+)/add_action_item/$',
        ProjectAddItemView.as_view(item_type='action item'),
        name='add_action_item'),
    url(r'^project/(?P<pk>\d+)/add_todo/$', ProjectAddTodoView.as_view(),
        name='project_add_todo'),
    url(r'^project/(?P<pk>\d+)/add_node/$', ProjectAddNodeView.as_view(),
        name='project_add_node'),
    url(r'^project/(?P<pk>\d+)/add_milestone/$',
        ProjectAddMilestoneView.as_view()),
    url(r'^project/(?P<pk>\d+)/add_update/$',
        ProjectAddStatusUpdateView.as_view(), name='project_add_update'),
    url(r'^project/(?P<pk>\d+)/edit/$', ProjectUpdateView.as_view()),
    url(r'^project/(?P<pk>\d+)/remove_user/(?P<username>\w+)/$',
        ProjectRemoveUserView.as_view()),
    url(r'^project/(?P<pk>\d+)/add_personnel/$',
        ProjectAddPersonnelView.as_view()),
    url(r'^project/(?P<pk>\d+)/tag/$', ProjectTagListView.as_view(),
        name='project_tag_list'),
    url(r'^project/(?P<pk>\d+)/tag/(?P<slug>[^/]+)/$',
        ProjectTagView.as_view(),
        name='project_tag'),

    url(r'^status/$', StatusUpdateListView.as_view()),
    url(r'^status/(?P<pk>\d+)/$', StatusUpdateUpdateView.as_view()),
    url(r'^status/(?P<pk>\d+)/delete/$', StatusUpdateDeleteView.as_view()),
    url(r'^report/', include('dmt.report.urls')),
    url(r'^user/$', UserListView.as_view(), name='user_list'),
    url(r'^user/(?P<pk>\w+)/$', UserDetailView.as_view(), name='user_detail'),
    url(r'^user/(?P<pk>\w+)/deactivate/$', DeactivateUserView.as_view(),
        name='user_deactivate'),
    url(r'^user/(?P<pk>\w+)/edit/$', UserUpdateView.as_view(),
        name='user_edit'),
    url(r'^user/(?P<pk>\w+)/owned/$', OwnedItemsView.as_view(),
        name='owned_items'),
    url(r'^user/(?P<pk>\w+)/timeline/$', UserTimeLineView.as_view(),
        name='user_timeline'),
    url(r'^tag/$', TagListView.as_view(), name='tag_list'),
    url(r'^tag/(?P<slug>[^/]+)/$', TagDetailView.as_view(), name='tag_detail'),
    url(r'^tag/(?P<slug>[^/]+)/merge/$', MergeTagView.as_view(),
        name='merge_tag'),
    url(r'^tag/(?P<slug>[^/]+)/delete/$', DeleteTagView.as_view(),
        name="delete_tag"),
    url(r'^dashboard/$', DashboardView.as_view(), name='project_dashboard'),
    url(r'^feeds/forum/rss/$', ForumFeed(), name='forum_feed'),
    url(r'^feeds/status/$', StatusUpdateFeed(), name='status_feed'),
    url(r'^feeds/project/(?P<pk>\d+)/$', ProjectFeed(), name='project_feed'),
    url(r'^_impersonate/', include('impersonate.urls')),
    url(r'^stats/$', TemplateView.as_view(template_name="stats.html")),
    url(r'^smoketest/', include('smoketest.urls')),
    url(r'^uploads/(?P<path>.*)$',
        django.views.static.serve, {'document_root': settings.MEDIA_ROOT}),
]

if settings.DEBUG:
    import debug_toolbar
    urlpatterns += [
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]

handler500 = 'dmt.main.views.server_error'

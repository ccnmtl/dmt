from django.contrib import admin
from dmt.main.models import StatusUpdate, UserProfile, InGroup, Project


@admin.register(InGroup)
class InGroupAdmin(admin.ModelAdmin):
    search_fields = ['username__username', 'username__fullname',
                     'grp__username']
    list_display = ('grp', 'username')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    search_fields = ['name']
    list_filter = ('caretaker_user',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['username', 'fullname']
    list_filter = ('grp', 'primary_group',)


@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    date_hierarchy = 'added'

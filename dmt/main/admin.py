from django.contrib import admin
from dmt.main.models import StatusUpdate, UserProfile, InGroup


admin.site.register(InGroup)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    search_fields = ['username', 'fullname']
    list_filter = ('grp', 'primary_group',)


@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    date_hierarchy = 'added'

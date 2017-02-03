from django.contrib import admin
from dmt.main.models import StatusUpdate, UserProfile


admin.site.register(UserProfile)


@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    date_hierarchy = 'added'

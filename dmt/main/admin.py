from django.contrib import admin
from dmt.main.models import StatusUpdate


@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    date_hierarchy = 'added'

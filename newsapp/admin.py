from django.contrib import admin
from .models import Advertisement


@admin.register(Advertisement)
class AdvertisementAdmin(admin.ModelAdmin):
    list_display = ("title", "advertiser_name", "status", "start_at", "end_at", "frequency")
    list_filter = ("status", "frequency", "page_target")
    search_fields = ("title", "advertiser_name")
    readonly_fields = ("created_at", "updated_at")

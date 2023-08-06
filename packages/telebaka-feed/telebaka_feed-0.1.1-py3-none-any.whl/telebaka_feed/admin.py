from django.contrib import admin

from telebaka_feed.models import VKFeed


@admin.register(VKFeed)
class VKFeedAdmin(admin.ModelAdmin):
    pass

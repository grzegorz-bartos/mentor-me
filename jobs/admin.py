from django.contrib import admin

from .models import Job, Proposal


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "user", "status", "created_at")
    list_filter = ("status",)
    search_fields = ("title", "description")


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    list_display = ("id", "job", "user", "price", "is_accepted", "created_at")
    list_filter = ("is_accepted",)

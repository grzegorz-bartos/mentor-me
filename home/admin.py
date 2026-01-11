from django.contrib import admin

from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ["user", "rating", "get_role_display", "created_at", "is_approved"]
    list_filter = ["rating", "is_approved", "created_at", "role_at_time"]
    search_fields = ["user__username", "user__email", "text"]
    list_editable = ["is_approved"]
    readonly_fields = ["created_at", "updated_at", "role_at_time"]

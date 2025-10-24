from django.contrib import admin

from .models import Availability, Booking, Listing


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ("id", "type", "title", "user", "price", "is_active", "created_at")
    list_filter = ("type", "is_active")
    search_fields = ("title", "description", "subject")


@admin.register(Availability)
class AvailabilityAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "day_of_week", "start_time", "end_time", "is_active")
    list_filter = ("day_of_week", "is_active")
    search_fields = ("listing__title",)


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("id", "listing", "student", "date", "start_time", "end_time", "status", "created_at")
    list_filter = ("status", "date")
    search_fields = ("listing__title", "student__username")

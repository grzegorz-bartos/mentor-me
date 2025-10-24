from debug_toolbar.toolbar import debug_toolbar_urls  # type: ignore
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from home import views as home_views
from jobs.views import (
    JobCreateView,
    JobDeleteView,
    JobDetailView,
    JobListView,
    accept_offer,
    submit_offer,
    take_job,
)
from listings.views import (
    CreateMentorListingView,
    CreateTutorListingView,
    DeleteAvailabilityView,
    ListingDeleteView,
    ListingDetailView,
    ListingListView,
    ManageAvailabilityView,
    MentorListView,
    MyBookingsView,
    UpdateBookingStatusView,
)
from subscriptions import views as subscriptions_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_views.HomeView.as_view(), name="home"),
    path("about/", home_views.AboutView.as_view(), name="about"),
    path("accounts/", include("users.urls")),
    path("accounts/", include("django.contrib.auth.urls")),
    path("listings/", ListingListView.as_view(), name="listings"),
    path(
        "listings/create/",
        CreateTutorListingView.as_view(),
        name="create-listing",
    ),
    path(
        "listings/<int:pk>/",
        ListingDetailView.as_view(),
        name="listing-detail",
    ),
    path(
        "listings/<int:pk>/delete/",
        ListingDeleteView.as_view(),
        name="listing-delete",
    ),
    path(
        "listings/<int:listing_id>/availability/",
        ManageAvailabilityView.as_view(),
        name="manage-availability",
    ),
    path(
        "availability/<int:pk>/delete/",
        DeleteAvailabilityView.as_view(),
        name="delete-availability",
    ),
    path("bookings/", MyBookingsView.as_view(), name="my-bookings"),
    path(
        "bookings/<int:booking_id>/status/<str:status>/",
        UpdateBookingStatusView.as_view(),
        name="update-booking-status",
    ),
    path(
        "mentoring/create/",
        CreateMentorListingView.as_view(),
        name="create-mentor-listing",
    ),
    path("jobs/", JobListView.as_view(), name="jobs"),
    path("jobs/create/", JobCreateView.as_view(), name="job-create"),
    path("jobs/<int:pk>/", JobDetailView.as_view(), name="job-detail"),
    path("jobs/<int:pk>/delete/", JobDeleteView.as_view(), name="job-delete"),
    path("jobs/<int:pk>/take/", take_job, name="job-take"),
    path("jobs/<int:pk>/offer/", submit_offer, name="job-offer"),
    path(
        "jobs/<int:job_id>/accept/<int:proposal_id>/",
        accept_offer,
        name="job-accept-offer",
    ),
    path("mentoring/", MentorListView.as_view(), name="mentors"),
    path("pricing/", subscriptions_views.PricingView.as_view(), name="pricing"),
    path(
        "pricing/change/<int:plan_id>/", # pricing/<int:plan_id>/change
        subscriptions_views.change_plan,
        name="change-plan",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += debug_toolbar_urls()

from debug_toolbar.toolbar import debug_toolbar_urls  # type: ignore
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

from home.views import (
    AboutView,
    ContactView,
    CreateTestimonialView,
    HomeView,
    UpdateTestimonialView,
)
from jobs.views import (
    AcceptOfferView,
    JobCreateView,
    JobDeleteView,
    JobDetailView,
    JobListView,
    SubmitOfferView,
    TakeJobView,
)
from listings.views import (
    CreateBookingView,
    CreateMentorListingView,
    CreateTutorListingView,
    DeleteAvailabilityView,
    ListingDeleteView,
    ListingDetailView,
    ListingListView,
    ManageAvailabilityView,
    MentorListView,
    MyBookingsView,
    StudentBookingsView,
    UpdateBookingStatusView,
    get_available_slots,
)
from subscriptions.views import ChangePlanView, PricingView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", HomeView.as_view(), name="home"),
    path("about/", AboutView.as_view(), name="about"),
    path(
        "about/testimonial/",
        CreateTestimonialView.as_view(),
        name="create-testimonial",
    ),
    path(
        "about/testimonial/update/",
        UpdateTestimonialView.as_view(),
        name="update-testimonial",
    ),
    path("contact/", ContactView.as_view(), name="contact"),
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
        "listings/<int:listing_id>/book/",
        CreateBookingView.as_view(),
        name="create-booking",
    ),
    path(
        "listings/<int:listing_id>/available-slots/",
        get_available_slots,
        name="available-slots",
    ),
    path("my-lessons/", StudentBookingsView.as_view(), name="student-bookings"),
    path(
        "mentoring/create/",
        CreateMentorListingView.as_view(),
        name="create-mentor-listing",
    ),
    path("jobs/", JobListView.as_view(), name="jobs"),
    path("jobs/create/", JobCreateView.as_view(), name="job-create"),
    path("jobs/<int:pk>/", JobDetailView.as_view(), name="job-detail"),
    path("jobs/<int:pk>/delete/", JobDeleteView.as_view(), name="job-delete"),
    path("jobs/<int:pk>/take/", TakeJobView.as_view(), name="job-take"),
    path("jobs/<int:pk>/offer/", SubmitOfferView.as_view(), name="job-offer"),
    path(
        "jobs/<int:job_id>/accept/<int:proposal_id>/",
        AcceptOfferView.as_view(),
        name="job-accept-offer",
    ),
    path("mentoring/", MentorListView.as_view(), name="mentors"),
    path("pricing/", PricingView.as_view(), name="pricing"),
    path(
        "pricing/change/<int:plan_id>/",
        ChangePlanView.as_view(),
        name="change-plan",
    ),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += debug_toolbar_urls()

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from core.mixins import CapabilityRequiredMixin

from .forms import AvailabilityForm, BookingForm, ListingCreationForm
from .models import Availability, Booking, Listing


class ListingListView(ListView):
    template_name = "listings.html"
    model = Listing
    context_object_name = "listings"
    paginate_by = 9  # <- pagination

    def get_queryset(self):
        qs = (
            super()
            .get_queryset()
            .select_related("user")
            .filter(type=Listing.ListingType.TUTOR, is_active=True)
            .order_by("-created_at")
        )
        q = self.request.GET.get("q")
        min_price = self.request.GET.get("min")
        max_price = self.request.GET.get("max")
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(subject__icontains=q)
                | Q(category__icontains=q)
            )
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        return qs


class MentorListView(ListView):
    template_name = "mentor-list.html"
    model = Listing
    context_object_name = "listings"
    paginate_by = 9  # <- pagination

    def get_queryset(self): # django-filter
        qs = (
            super()
            .get_queryset()
            .select_related("user")
            .filter(type=Listing.ListingType.MENTOR, is_active=True)
            .order_by("-created_at")
        )
        q = self.request.GET.get("q")
        min_price = self.request.GET.get("min")
        max_price = self.request.GET.get("max")
        if q:
            qs = qs.filter(
                Q(title__icontains=q)
                | Q(description__icontains=q)
                | Q(subject__icontains=q)
                | Q(category__icontains=q)
            )
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        return qs


class CreateTutorListingView(LoginRequiredMixin, CreateView):
    template_name = "create-listing.html"
    form_class = ListingCreationForm
    model = Listing
    success_url = reverse_lazy("listings")

    def dispatch(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.shortcuts import redirect

        if not request.user.can_post_tutor:
            messages.error(request, "You need to be a Tutor or higher to create tutor listings.")
            return redirect("pricing")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listing_type'] = 'tutor'
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.type = Listing.ListingType.TUTOR
        return super().form_valid(form)


class CreateMentorListingView(LoginRequiredMixin, CreateView):
    template_name = "create-listing.html"
    form_class = ListingCreationForm
    model = Listing
    success_url = reverse_lazy("mentors")

    def dispatch(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.shortcuts import redirect

        if not request.user.can_post_mentor:
            messages.error(request, "You need to be a Mentor to create mentor listings.")
            return redirect("pricing")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['listing_type'] = 'mentor'
        return context

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.type = Listing.ListingType.MENTOR
        return super().form_valid(form)


class ListingDetailView(DetailView):
    model = Listing
    template_name = "listing-detail.html"
    context_object_name = "listing"

    def get_queryset(self):
        return super().get_queryset().select_related("user").filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["availabilities"] = self.object.availabilities.filter(is_active=True)
        context["booking_form"] = BookingForm()
        return context


class ListingDeleteView(LoginRequiredMixin, DeleteView):
    model = Listing
    template_name = "listing_confirm_delete.html"
    success_url = reverse_lazy("profile")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Listing deleted successfully.")
        return super().delete(request, *args, **kwargs)


class ManageAvailabilityView(LoginRequiredMixin, ListView):
    model = Availability
    template_name = "manage-availability.html"
    context_object_name = "availabilities"

    def get_queryset(self):
        self.listing = get_object_or_404(
            Listing, pk=self.kwargs["listing_id"], user=self.request.user
        )
        return self.listing.availabilities.filter(is_active=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["listing"] = self.listing
        context["form"] = AvailabilityForm()
        return context

    def post(self, request, *args, **kwargs):
        self.listing = get_object_or_404(
            Listing, pk=self.kwargs["listing_id"], user=request.user
        )
        form = AvailabilityForm(request.POST)
        if form.is_valid():
            availability = form.save(commit=False)
            availability.listing = self.listing
            availability.save()
            messages.success(request, "Availability added successfully.")
            return redirect("manage-availability", listing_id=self.listing.id)

        self.object_list = self.get_queryset()
        context = self.get_context_data()
        context["form"] = form
        return self.render_to_response(context)


class DeleteAvailabilityView(LoginRequiredMixin, DeleteView):
    model = Availability

    def get_queryset(self):
        return super().get_queryset().filter(listing__user=self.request.user)

    def get_success_url(self):
        return reverse("manage-availability", kwargs={"listing_id": self.object.listing.id})

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Availability deleted successfully.")
        return super().delete(request, *args, **kwargs)


class MyBookingsView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "my-bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return Booking.objects.filter(listing__user=self.request.user).select_related(
            "student", "listing"
        )


class UpdateBookingStatusView(LoginRequiredMixin, View):
    def post(self, request, booking_id, status):
        booking = get_object_or_404(
            Booking, pk=booking_id, listing__user=request.user
        )
        if status in dict(Booking.Status.choices):
            booking.status = status
            booking.save()
            messages.success(request, f"Booking {status}.")
        return redirect("my-bookings")


class CreateBookingView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = "create-booking.html"

    def get_listing(self):
        if not hasattr(self, "_listing"):
            self._listing = get_object_or_404(Listing, pk=self.kwargs["listing_id"])
        return self._listing

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["listing"] = self.get_listing()
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["listing"] = self.get_listing()
        context["availabilities"] = self.get_listing().availabilities.filter(is_active=True)
        return context

    def form_valid(self, form):
        from datetime import datetime, timedelta

        form.instance.listing = self.get_listing()
        form.instance.student = self.request.user

        start_time = form.cleaned_data["start_time"]
        duration_hours = form.cleaned_data["duration_hours"]

        start_dt = datetime.combine(datetime.today(), start_time)
        end_dt = start_dt + timedelta(hours=duration_hours)
        form.instance.end_time = end_dt.time()

        messages.success(self.request, "Booking request submitted successfully!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("student-bookings")


class StudentBookingsView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "student-bookings.html"
    context_object_name = "bookings"

    def get_queryset(self):
        return Booking.objects.filter(student=self.request.user).select_related(
            "listing", "listing__user"
        )

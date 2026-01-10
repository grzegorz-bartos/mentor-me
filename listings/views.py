import calendar
from datetime import date, datetime, time, timedelta
from types import SimpleNamespace

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView, ListView
from django_filters.views import FilterView

from .filters import ListingFilter
from .forms import AvailabilityForm, BookingForm, ListingCreationForm
from .models import Availability, Booking, Listing


class ListingListView(FilterView):
    template_name = "listings.html"
    model = Listing
    context_object_name = "listings"
    paginate_by = 9
    filterset_class = ListingFilter

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("user")
            .filter(type=Listing.ListingType.TUTOR, is_active=True)
            .order_by("-created_at")
        )


class MentorListView(FilterView):
    template_name = "mentor-list.html"
    model = Listing
    context_object_name = "listings"
    paginate_by = 9
    filterset_class = ListingFilter

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("user")
            .filter(type=Listing.ListingType.MENTOR, is_active=True)
            .order_by("-created_at")
        )


class CreateTutorListingView(LoginRequiredMixin, CreateView):
    template_name = "create-listing.html"
    form_class = ListingCreationForm
    model = Listing
    success_url = reverse_lazy("listings")

    def dispatch(self, request, *args, **kwargs):
        from django.contrib import messages
        from django.shortcuts import redirect

        if request.user.is_authenticated and not request.user.can_post_tutor:
            messages.error(
                request, "You need to be a Tutor or higher to create tutor listings."
            )
            return redirect("pricing")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["listing_type"] = "tutor"
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

        if request.user.is_authenticated and not request.user.can_post_mentor:
            messages.error(
                request, "You need to be a Mentor to create mentor listings."
            )
            return redirect("pricing")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["listing_type"] = "mentor"
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
        context["availabilities"] = self.object.user.availabilities.filter(
            is_active=True
        )
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
        return self.request.user.availabilities.filter(is_active=True)

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
            availability.user = request.user
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
        return super().get_queryset().filter(user=self.request.user)

    def get_success_url(self):
        listing = self.request.user.listings.first()
        if listing:
            return reverse("manage-availability", kwargs={"listing_id": listing.id})
        return reverse("profile")

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
        booking = get_object_or_404(Booking, pk=booking_id, listing__user=request.user)
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
        listing = self.get_listing()
        context["listing"] = listing
        context["availabilities"] = listing.user.availabilities.filter(is_active=True)

        # Add current year and month for calendar
        today = date.today()
        year, month = today.year, today.month
        context["current_year"] = year
        context["current_month"] = month

        # Calculate availability counts for each day in the month
        availability_counts = {}
        _, num_days = calendar.monthrange(year, month)

        for day in range(1, num_days + 1):
            check_date = date(year, month, day)
            if check_date >= today:  # Only check future dates
                slot_count = self._count_available_slots(listing, check_date)
                availability_counts[day] = slot_count

        context["availability_counts"] = availability_counts
        return context

    def _count_available_slots(self, listing, check_date):
        """Count available time slots for a given date"""
        day_of_week = check_date.weekday()
        availabilities = listing.user.availabilities.filter(
            day_of_week=day_of_week, is_active=True
        )

        if not availabilities.exists():
            default_availability = SimpleNamespace(
                start_time=time(6, 0), end_time=time(23, 0)
            )
            availabilities = [default_availability]

        existing_bookings = Booking.objects.filter(
            listing=listing,
            date=check_date,
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        ).values_list("start_time", "end_time")

        slot_count = 0
        for availability in availabilities:
            current_time = datetime.combine(check_date, availability.start_time)
            end_time = datetime.combine(check_date, availability.end_time)

            while current_time < end_time:
                is_available = True
                slot_end = current_time + timedelta(hours=1)

                for booking_start, booking_end in existing_bookings:
                    booking_start_dt = datetime.combine(check_date, booking_start)
                    booking_end_dt = datetime.combine(check_date, booking_end)

                    if current_time < booking_end_dt and slot_end > booking_start_dt:
                        is_available = False
                        break

                if is_available:
                    slot_count += 1

                current_time += timedelta(hours=1)

        return slot_count

    def form_valid(self, form):
        form.instance.listing = self.get_listing()
        form.instance.student = self.request.user

        start_time = form.cleaned_data["start_time"]
        booking_date = form.cleaned_data["date"]

        # All bookings are fixed 1-hour sessions
        duration_hours = 1
        form.instance.duration_hours = duration_hours

        start_dt = datetime.combine(datetime.today(), start_time)
        end_dt = start_dt + timedelta(hours=duration_hours)
        form.instance.end_time = end_dt.time()

        conflicting_bookings = Booking.objects.filter(
            listing=self.get_listing(),
            date=booking_date,
            status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
        )

        for booking in conflicting_bookings:
            booking_start = datetime.combine(booking_date, booking.start_time)
            booking_end = datetime.combine(booking_date, booking.end_time)
            new_start = datetime.combine(booking_date, start_time)
            new_end = datetime.combine(booking_date, form.instance.end_time)

            if new_start < booking_end and new_end > booking_start:
                messages.error(
                    self.request,
                    "This time slot conflicts with an existing booking. Please choose a different time.",
                )
                return self.form_invalid(form)

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


def get_available_slots(request, listing_id):
    date_str = request.GET.get("date")
    if not date_str:
        return JsonResponse({"slots": []})

    try:
        selected_date = datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        return JsonResponse({"slots": []})

    listing = get_object_or_404(Listing, pk=listing_id)
    day_of_week = selected_date.weekday()

    availabilities = listing.user.availabilities.filter(
        day_of_week=day_of_week, is_active=True
    )

    if not availabilities.exists():
        default_availability = SimpleNamespace(
            start_time=time(6, 0), end_time=time(23, 0)
        )
        availabilities = [default_availability]

    existing_bookings = Booking.objects.filter(
        listing=listing,
        date=selected_date,
        status__in=[Booking.Status.PENDING, Booking.Status.CONFIRMED],
    ).values_list("start_time", "end_time")

    from django.utils import timezone

    now = timezone.now()
    now_local = timezone.localtime(now)
    booking_cutoff_local = now_local + timedelta(minutes=10)

    all_slots = []
    for availability in availabilities:
        current_time = datetime.combine(selected_date, availability.start_time)
        end_time = datetime.combine(selected_date, availability.end_time)

        while current_time < end_time:
            time_value = current_time.time()
            is_available = True

            slot_datetime_naive = datetime.combine(selected_date, time_value)
            slot_datetime_aware = timezone.make_aware(slot_datetime_naive)
            slot_datetime_local = timezone.localtime(slot_datetime_aware)

            if slot_datetime_local < booking_cutoff_local:
                current_time += timedelta(hours=1)
                continue

            slot_end = current_time + timedelta(hours=1)

            for booking_start, booking_end in existing_bookings:
                booking_start_dt = datetime.combine(selected_date, booking_start)
                booking_end_dt = datetime.combine(selected_date, booking_end)

                if current_time < booking_end_dt and slot_end > booking_start_dt:
                    is_available = False
                    break

            hour = current_time.hour
            minute = current_time.minute
            display = f"{hour % 12 or 12}:{minute:02d} {'AM' if hour < 12 else 'PM'}"

            all_slots.append(
                {
                    "value": time_value.strftime("%H:%M"),
                    "display": display,
                    "is_available": is_available,
                }
            )

            current_time += timedelta(hours=1)

    return JsonResponse({"slots": all_slots})

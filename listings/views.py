from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView

from core.mixins import CapabilityRequiredMixin

from .forms import ListingCreationForm
from .models import Listing


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


class ListingDeleteView(LoginRequiredMixin, DeleteView):
    model = Listing
    template_name = "listing_confirm_delete.html"
    success_url = reverse_lazy("profile")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Listing deleted successfully.")
        return super().delete(request, *args, **kwargs)

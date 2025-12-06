from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from home.forms import ContactForm
from jobs.models import Job
from listings.models import Listing
from users.models import Account


class HomeView(TemplateView):
    template_name = "home.html"  # home.html

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["listings"] = Listing.objects.order_by("id")[:3]
        context["listings"] = Listing.objects.select_related("user").order_by("id")[:3]

        context["total_students"] = Account.objects.filter(
            role_level=Account.Role.STUDENT
        ).count()
        context["total_tutors"] = Account.objects.filter(
            role_level__gte=Account.Role.TUTOR
        ).count()
        context["total_mentors"] = Account.objects.filter(
            role_level__gte=Account.Role.MENTOR
        ).count()
        context["open_jobs"] = Job.objects.filter(status=Job.Status.OPEN).count()

        return context


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["listings"] = Listing.objects.order_by("id")[:3]
        context["listings"] = Listing.objects.select_related("user").order_by("id")[:3]

        context["total_students"] = Account.objects.filter(
            role_level=Account.Role.STUDENT
        ).count()
        context["total_tutors"] = Account.objects.filter(
            role_level__gte=Account.Role.TUTOR
        ).count()
        context["total_mentors"] = Account.objects.filter(
            role_level__gte=Account.Role.MENTOR
        ).count()
        context["open_jobs"] = Job.objects.filter(status=Job.Status.OPEN).count()

        return context


class ContactView(FormView):
    template_name = "contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact")

    def form_valid(self, form):
        # Extract form data
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]
        subject = form.cleaned_data["subject"]
        message = form.cleaned_data["message"]

        # TODO: Send email or save to database
        # For now, just display a success message
        messages.success(
            self.request,
            f"Thank you for contacting us, {name}! We'll get back to you at {email} soon.",
        )

        return super().form_valid(form)

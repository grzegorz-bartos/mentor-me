from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView, TemplateView

from home.forms import ContactForm, TestimonialForm
from home.models import Testimonial
from jobs.models import Job
from listings.models import Listing
from users.models import Account


class HomeView(TemplateView):
    template_name = "home.html"  # home.html

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
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

        context["testimonials"] = Testimonial.objects.filter(
            is_approved=True
        ).select_related("user")
        context["testimonial_form"] = TestimonialForm()

        return context


class ContactView(FormView):
    template_name = "contact.html"
    form_class = ContactForm
    success_url = reverse_lazy("contact")

    def form_valid(self, form):
        name = form.cleaned_data["name"]
        email = form.cleaned_data["email"]

        messages.success(
            self.request,
            f"Thank you for contacting us, {name}! We'll get back to you at {email} soon.",
        )

        return super().form_valid(form)


class CreateTestimonialView(LoginRequiredMixin, CreateView):
    model = Testimonial
    form_class = TestimonialForm
    success_url = reverse_lazy("about")

    def dispatch(self, request, *args, **kwargs):
        if hasattr(request.user, "testimonial"):
            messages.warning(request, "You have already submitted a testimonial.")
            return redirect("about")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.role_at_time = self.request.user.role_level
        messages.success(self.request, "Thank you for sharing your opinion!")
        return super().form_valid(form)


class UpdateTestimonialView(LoginRequiredMixin, TemplateView):
    def post(self, request):
        if not hasattr(request.user, "testimonial"):
            messages.error(request, "You don't have a testimonial to update.")
            return redirect("about")

        testimonial = request.user.testimonial
        form = TestimonialForm(request.POST, instance=testimonial)
        if form.is_valid():
            form.save()
            messages.success(request, "Your testimonial has been updated!")
        else:
            messages.error(request, "There was an error updating your testimonial.")

        return redirect("about")

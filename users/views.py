from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from jobs.models import Job, Proposal
from listings.models import Listing
from subscriptions.models import Plan, Subscription

from .forms import AccountCreationForm


class SignUpView(CreateView):
    form_class = AccountCreationForm
    template_name = "signup.html"
    success_url = reverse_lazy("login")


class LoginView(DjangoLoginView):
    template_name = "login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        next_url = self.request.GET.get("next") or self.request.POST.get("next")
        if next_url:
            return next_url
        return super().get_success_url()


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = "profile.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user

        # plan/subscription info
        sub = Subscription.objects.filter(user=user).select_related("plan").first()
        context["subscription"] = sub
        context["current_plan_level"] = getattr(user, "role_level", None)
        context["plans"] = Plan.objects.order_by("level")

        # user's content
        context["my_listings"] = Listing.objects.filter(user=user).order_by(
            "-created_at"
        )[:20]
        context["my_jobs"] = (
            Job.objects.filter(user=user)
            .order_by("-created_at")
            .prefetch_related("proposals")
        )
        context["my_offers"] = (
            Proposal.objects.filter(user=user)
            .select_related("job")
            .order_by("-created_at")[:20]
        )
        context["reviews_received"] = user.reviews_received.select_related(
            "reviewer", "booking"
        ).order_by("-created_at")[:10]
        context["reviews_given"] = user.reviews_given.select_related(
            "reviewed_user", "booking"
        ).order_by("-created_at")[:10]

        return context

    def post(self, request, *args, **kwargs):
        field = request.POST.get("field")
        user = request.user

        if field in ["username", "email"]:
            value = request.POST.get(field)
            if value:
                setattr(user, field, value)
                try:
                    user.save()
                    messages.success(
                        request, f"{field.capitalize()} updated successfully!"
                    )
                except Exception as e:
                    messages.error(request, f"Error updating {field}: {str(e)}")
            else:
                messages.error(request, f"{field.capitalize()} cannot be empty")

        return redirect("profile")

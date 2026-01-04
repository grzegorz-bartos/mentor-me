from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView, TemplateView

from jobs.models import Job, Proposal
from listings.models import Listing
from subscriptions.models import Plan, Subscription

from .forms import AccountCreationForm


class SignUpView(CreateView):
    form_class = AccountCreationForm
    template_name = "signup.html"
    success_url = reverse_lazy("login")  # after sign up -> login page


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
        ctx = super().get_context_data(**kwargs)
        user = self.request.user

        # plan/subscription info
        sub = Subscription.objects.filter(user=user).select_related("plan").first()
        ctx["subscription"] = sub
        ctx["current_plan_level"] = getattr(user, "role_level", None)
        ctx["plans"] = Plan.objects.order_by("level")

        # user’s content
        ctx["my_listings"] = Listing.objects.filter(user=user).order_by("-created_at")[
            :20
        ]
        ctx["my_jobs"] = (
            Job.objects.filter(user=user)
            .order_by("-created_at")
            .prefetch_related("proposals")
        )
        ctx["my_offers"] = (
            Proposal.objects.filter(user=user)
            .select_related("job")
            .order_by("-created_at")[:20]
        )
        return ctx

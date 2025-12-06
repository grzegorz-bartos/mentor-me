from typing import Any

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import url_has_allowed_host_and_scheme
from django.views import View
from django.views.generic import TemplateView

from users.models import Account

from .models import Plan, Subscription


class PricingView(TemplateView):
    template_name = "pricing.html"

    def get_context_data(self, **kwargs) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["plans"] = Plan.objects.order_by("level")
        user = self.request.user
        ctx["current_plan_level"] = (
            getattr(user, "role_level", None) if user.is_authenticated else None
        )
        return ctx


class ChangePlanView(LoginRequiredMixin, View):
    def post(self, request, plan_id):
        plan = get_object_or_404(Plan, pk=plan_id)
        acc: Account = request.user

        if acc.role_level == plan.level:
            messages.info(request, f"You're already on the {plan.name} plan.")
            return self._redirect_back(request)

        with transaction.atomic():
            acc.role_level = plan.level
            acc.save(update_fields=["role_level"])

            sub, _ = Subscription.objects.select_for_update().get_or_create(
                user=acc, defaults={"plan": plan}
            )
            sub.plan = plan
            sub.is_active = True
            sub.save(update_fields=["plan", "is_active"])

        messages.success(request, f"Plan changed to {plan.name}.")
        return self._redirect_back(request)

    def _redirect_back(self, request):
        next_url = (
            request.GET.get("next") or request.META.get("HTTP_REFERER") or "/pricing/"
        )
        if not url_has_allowed_host_and_scheme(
            next_url, allowed_hosts={request.get_host()}
        ):
            next_url = "/pricing/"
        return redirect(next_url)

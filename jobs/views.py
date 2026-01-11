from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, DetailView
from django_filters.views import FilterView

from .filters import JobFilter
from .forms import JobForm, ProposalForm
from .models import Job, Proposal


class JobListView(FilterView):
    template_name = "job-list.html"
    model = Job
    context_object_name = "jobs"
    paginate_by = 9
    filterset_class = JobFilter

    def get_queryset(self):
        return super().get_queryset().select_related("user").order_by("-created_at")


class JobCreateView(LoginRequiredMixin, CreateView):
    template_name = "job-create.html"
    form_class = JobForm
    model = Job
    success_url = reverse_lazy("jobs")

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class JobDetailView(DetailView):
    model = Job
    template_name = "job-detail.html"
    context_object_name = "job"

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .select_related("user")
            .prefetch_related("proposals__user")
        )


class SubmitOfferView(LoginRequiredMixin, View):
    def get(self, request, pk):
        job = get_object_or_404(Job, pk=pk, status=Job.Status.OPEN)

        if job.user == request.user:
            messages.error(request, "You cannot submit an offer to your own job.")
            return redirect("job-detail", pk=job.pk)

        if not request.user.can_take_jobs:
            messages.error(request, "Upgrade to Freelancer to submit offers.")
            return redirect("pricing")

        form = ProposalForm()
        return render(request, "job-offer.html", {"form": form, "job": job})

    def post(self, request, pk):
        job = get_object_or_404(Job, pk=pk, status=Job.Status.OPEN)

        if job.user == request.user:
            messages.error(request, "You cannot submit an offer to your own job.")
            return redirect("job-detail", pk=job.pk)

        if not request.user.can_take_jobs:
            messages.error(request, "Upgrade to Freelancer to submit offers.")
            return redirect("pricing")

        form = ProposalForm(request.POST)
        if form.is_valid():
            Proposal.objects.update_or_create(
                job=job, user=request.user, defaults=form.cleaned_data
            )
            messages.success(request, "Offer submitted.")
            return redirect("jobs")

        return render(request, "job-offer.html", {"form": form, "job": job})


class AcceptOfferView(LoginRequiredMixin, View):
    def post(self, request, job_id, proposal_id):
        job = get_object_or_404(Job, pk=job_id)
        if job.user != request.user:
            messages.error(request, "Only the job owner can accept offers.")
            return redirect("jobs")
        prop = get_object_or_404(Proposal, pk=proposal_id, job=job)
        Proposal.objects.filter(job=job).update(is_accepted=False)
        prop.is_accepted = True
        prop.save(update_fields=["is_accepted"])
        job.status = Job.Status.IN_PROGRESS
        job.save(update_fields=["status"])
        messages.success(request, "Offer accepted.")
        return redirect("jobs")


class JobDeleteView(LoginRequiredMixin, DeleteView):
    model = Job
    template_name = "job_confirm_delete.html"
    success_url = reverse_lazy("profile")

    def get_queryset(self):
        return super().get_queryset().filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        messages.success(request, "Job deleted successfully.")
        return super().delete(request, *args, **kwargs)

from django import forms

from .models import Job, Proposal


class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ["title", "description", "budget", "subject"]


class ProposalForm(forms.ModelForm):
    class Meta:
        model = Proposal
        fields = ["message", "price"]

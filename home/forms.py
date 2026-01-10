from django import forms

from .models import Testimonial


class TestimonialForm(forms.ModelForm):
    class Meta:
        model = Testimonial
        fields = ["rating", "text"]
        widgets = {
            "rating": forms.RadioSelect(
                choices=[(5, "5"), (4, "4"), (3, "3"), (2, "2"), (1, "1")],
                attrs={"class": "rating-input"},
            ),
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Share your experience with MentorMe...",
                    "rows": 4,
                }
            ),
        }


class ContactForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Your Name"}
        ),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={"class": "form-control", "placeholder": "Your Email"}
        ),
    )
    subject = forms.CharField(
        max_length=200,
        widget=forms.TextInput(
            attrs={"class": "form-control", "placeholder": "Subject"}
        ),
    )
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={"class": "form-control", "placeholder": "Message", "rows": 6}
        ),
    )

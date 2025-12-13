from django import forms

from .models import Availability, Booking, Listing


class ListingCreationForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            "title",
            "description",
            "price",
            "rate_unit",
            "subject",
            "category",
            "max_hours_per_booking",
        ]


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = Availability
        fields = ["day_of_week", "start_time", "end_time"]
        widgets = {
            "start_time": forms.TimeInput(attrs={"type": "time"}),
            "end_time": forms.TimeInput(attrs={"type": "time"}),
        }


class BookingForm(forms.ModelForm):
    def _generate_time_choices():
        times = []
        # Generate hourly slots only (no 15-minute increments)
        for hour in range(6, 23):
            time_str = f"{hour:02d}:00"
            display = f"{hour % 12 or 12}:00 {'AM' if hour < 12 else 'PM'}"
            times.append((time_str, display))
        return times

    start_time = forms.ChoiceField(
        choices=_generate_time_choices(),
        label="Start Time (1 hour session)",
        widget=forms.Select(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Booking
        fields = ["date", "start_time", "notes"]
        widgets = {
            "date": forms.HiddenInput(),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.listing = kwargs.pop("listing", None)
        super().__init__(*args, **kwargs)

    def clean_start_time(self):
        from datetime import datetime

        time_str = self.cleaned_data.get("start_time")
        if time_str:
            return datetime.strptime(time_str, "%H:%M").time()
        return time_str

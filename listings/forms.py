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
        for hour in range(6, 23):
            for minute in [0, 15, 30, 45]:
                time_str = f"{hour:02d}:{minute:02d}"
                display = f"{hour % 12 or 12}:{minute:02d} {'AM' if hour < 12 else 'PM'}"
                times.append((time_str, display))
        return times

    start_time = forms.ChoiceField(
        choices=_generate_time_choices(),
        label="Start Time",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    duration_hours = forms.ChoiceField(
        choices=[(i, f"{i} hour{'s' if i > 1 else ''}") for i in range(1, 9)],
        label="Duration",
        widget=forms.Select(attrs={"class": "form-control"})
    )

    class Meta:
        model = Booking
        fields = ["date", "start_time", "duration_hours", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "notes": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        self.listing = kwargs.pop("listing", None)
        super().__init__(*args, **kwargs)
        if self.listing:
            max_hours = int(self.listing.max_hours_per_booking)
            self.fields["duration_hours"].choices = [
                (i, f"{i} hour{'s' if i > 1 else ''}") for i in range(1, max_hours + 1)
            ]

    def clean_start_time(self):
        from datetime import datetime
        time_str = self.cleaned_data.get("start_time")
        if time_str:
            return datetime.strptime(time_str, "%H:%M").time()
        return time_str

    def clean_duration_hours(self):
        duration = self.cleaned_data.get("duration_hours")
        if duration:
            return int(duration)
        return duration

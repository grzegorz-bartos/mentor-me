from django import forms

from .models import Availability, Booking, Listing, Review


class ListingCreationForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = [
            "title",
            "description",
            "price",
            "subject",
            "category",
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
            parsed_time = datetime.strptime(time_str, "%H:%M").time()

            if parsed_time.minute != 0 or parsed_time.second != 0:
                raise forms.ValidationError(
                    "Bookings must be on the hour. Minutes and seconds must be :00."
                )

            if parsed_time.hour < 6 or parsed_time.hour >= 23:
                raise forms.ValidationError(
                    "Booking times must be between 6:00 AM and 10:00 PM."
                )

            return parsed_time
        return time_str

    def clean(self):
        from datetime import datetime, timedelta

        from django.utils import timezone

        cleaned_data = super().clean()
        date = cleaned_data.get("date")
        start_time = cleaned_data.get("start_time")

        if date and start_time:
            booking_datetime_naive = datetime.combine(date, start_time)
            booking_datetime_aware = timezone.make_aware(booking_datetime_naive)
            booking_datetime_local = timezone.localtime(booking_datetime_aware)

            now = timezone.now()
            now_local = timezone.localtime(now)
            booking_cutoff_local = now_local + timedelta(minutes=10)

            if booking_datetime_local < booking_cutoff_local:
                raise forms.ValidationError(
                    "Bookings must be made at least 10 minutes in advance. Please select a later time."
                )

        return cleaned_data


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.RadioSelect(
                choices=[(5, "5"), (4, "4"), (3, "3"), (2, "2"), (1, "1")],
                attrs={"class": "rating-input"},
            ),
            "comment": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "placeholder": "Share your experience...",
                    "rows": 4,
                }
            ),
        }

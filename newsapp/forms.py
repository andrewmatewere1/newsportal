from datetime import timedelta

from django import forms
from django.utils import timezone

from .models import Advertisement


class AdvertisementForm(forms.ModelForm):
    DURATION_CHOICES = [
        ("24h", "24 hours"),
        ("7d", "7 days (1 week)"),
        ("30d", "30 days (approximately 1 month)"),
        ("custom", "Custom end date and time"),
    ]
    duration_preset = forms.ChoiceField(
        choices=DURATION_CHOICES,
        initial="7d",
        required=False,
        label="Campaign duration",
        help_text="Choose a preset or choose Custom to set the exact end date/time.",
    )

    start_at = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}, format="%Y-%m-%dT%H:%M"),
    )
    end_at = forms.DateTimeField(
        input_formats=["%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M:%S"],
        widget=forms.DateTimeInput(attrs={"type": "datetime-local", "class": "form-control"}, format="%Y-%m-%dT%H:%M"),
        required=False,
    )

    class Meta:
        model = Advertisement
        fields = [
            "title", "advertiser_name", "image", "target_url", "display_type",
            "status", "start_at", "end_at", "duration_preset", "frequency", "page_target",
            "delay_seconds", "priority",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control"}),
            "advertiser_name": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "image/*"}),
            "target_url": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://advertiser.example"}),
            "display_type": forms.Select(attrs={"class": "form-select"}),
            "status": forms.Select(attrs={"class": "form-select"}),
            "frequency": forms.Select(attrs={"class": "form-select"}),
            "page_target": forms.Select(attrs={"class": "form-select"}),
            "delay_seconds": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 60}),
            "priority": forms.NumberInput(attrs={"class": "form-control", "min": 0}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["duration_preset"].widget.attrs.update({"class": "form-select"})
        if self.instance and self.instance.pk:
            self.fields["duration_preset"].initial = "custom"
        else:
            self.fields["start_at"].initial = timezone.localtime().replace(second=0, microsecond=0).strftime("%Y-%m-%dT%H:%M")

    def clean_image(self):
        image = self.cleaned_data.get("image")
        if image and getattr(image, "size", 0) > 5 * 1024 * 1024:
            raise forms.ValidationError("Advertisement images must be 5 MB or smaller.")
        return image

    def clean(self):
        cleaned = super().clean()
        start = cleaned.get("start_at")
        end = cleaned.get("end_at")
        preset = cleaned.get("duration_preset")
        if start and preset in {"24h", "7d", "30d"}:
            hours = {"24h": 24, "7d": 24 * 7, "30d": 24 * 30}[preset]
            cleaned["end_at"] = start + timedelta(hours=hours)
        elif start and preset == "custom":
            if not end:
                self.add_error("end_at", "Set an end date and time for a custom campaign.")
            elif end <= start:
                self.add_error("end_at", "End date/time must be later than start date/time.")
        if cleaned.get("delay_seconds") is not None and not 0 <= cleaned["delay_seconds"] <= 60:
            self.add_error("delay_seconds", "Popup delay must be between 0 and 60 seconds.")
        return cleaned

# Generated for the advertisement campaign management feature.
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("newsapp", "0008_alter_customuser_user_type"),
    ]

    operations = [
        migrations.CreateModel(
            name="Advertisement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(max_length=200)),
                ("advertiser_name", models.CharField(blank=True, max_length=200)),
                ("image", models.ImageField(upload_to="adverts/%Y/%m/")),
                ("target_url", models.URLField(blank=True, max_length=1000)),
                ("display_type", models.CharField(choices=[("popup", "Popup")], default="popup", max_length=20)),
                ("status", models.CharField(choices=[("draft", "Draft"), ("active", "Active"), ("paused", "Paused")], default="draft", max_length=20)),
                ("start_at", models.DateTimeField()),
                ("end_at", models.DateTimeField()),
                ("frequency", models.CharField(choices=[("session", "Once per browser session"), ("24h", "Once every 24 hours per browser"), ("every_visit", "Every eligible visit")], default="24h", max_length=20)),
                ("page_target", models.CharField(choices=[("all", "All public pages"), ("home", "Homepage only"), ("articles", "News article pages")], default="all", max_length=20)),
                ("delay_seconds", models.PositiveSmallIntegerField(default=3, help_text="Seconds to wait before showing a popup (0–60).")),
                ("priority", models.PositiveSmallIntegerField(default=100, help_text="Lower numbers are shown first when campaigns overlap.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("created_by", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="advertisement_campaigns", to="newsapp.customuser")),
            ],
            options={"ordering": ["priority", "-created_at"]},
        ),
        migrations.AddIndex(
            model_name="advertisement",
            index=models.Index(fields=["status", "start_at", "end_at"], name="newsapp_adv_status_3d2f9a_idx"),
        ),
        migrations.AddIndex(
            model_name="advertisement",
            index=models.Index(fields=["display_type", "page_target"], name="newsapp_adv_display_3f0a71_idx"),
        ),
    ]

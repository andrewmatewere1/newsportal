
from django.db import models
from django.core.validators import RegexValidator
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class CustomUser(AbstractUser):
    USER = (
        (1, "admin"),
        (2, "subadmin"),
    )
    user_type = models.CharField(choices=USER, max_length=50, default=1)

    profile_pic = models.ImageField(upload_to='media/profile_pic')

class Category(models.Model):
    catname = models.CharField(max_length=200)
    catdes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.catname

class Subcategory(models.Model):
    cat_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcatname = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.subcatname


class News(models.Model):
    cat_id = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory_id = models.ForeignKey(Subcategory, on_delete=models.CASCADE)
    posttitle = models.TextField(blank=True)
    postdetails = models.TextField(blank=True)
    status = models.CharField(max_length=50)
    postimage = models.ImageField(upload_to='media/news')
    postedby = models.CharField(max_length=50)
    posted_date= models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    updatedby = models.CharField(max_length=50)

class Page(models.Model):
    pagetitle = models.CharField(max_length=250)
    address = models.CharField(max_length=250)
    aboutus = models.TextField()
    email = models.EmailField(max_length=200)
    mobilenumber = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

class Comments(models.Model):
    news_id = models.ForeignKey(News, on_delete=models.CASCADE)
    comment = models.TextField()
    name = models.CharField(max_length=250)
    email = models.CharField(max_length=250)
    status = models.CharField(max_length=250,blank=True)
    posted_date= models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)




class Advertisement(models.Model):
    """A scheduled advert campaign displayed on the public news website."""

    DISPLAY_POPUP = "popup"
    DISPLAY_BANNER = "banner"
    DISPLAY_CHOICES = [
        (DISPLAY_POPUP, "Popup"),
    ]

    STATUS_DRAFT = "draft"
    STATUS_ACTIVE = "active"
    STATUS_PAUSED = "paused"
    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_ACTIVE, "Active"),
        (STATUS_PAUSED, "Paused"),
    ]

    FREQUENCY_SESSION = "session"
    FREQUENCY_24_HOURS = "24h"
    FREQUENCY_EVERY_VISIT = "every_visit"
    FREQUENCY_CHOICES = [
        (FREQUENCY_SESSION, "Once per browser session"),
        (FREQUENCY_24_HOURS, "Once every 24 hours per browser"),
        (FREQUENCY_EVERY_VISIT, "Every eligible visit"),
    ]

    PAGE_ALL = "all"
    PAGE_HOME = "home"
    PAGE_ARTICLES = "articles"
    PAGE_CHOICES = [
        (PAGE_ALL, "All public pages"),
        (PAGE_HOME, "Homepage only"),
        (PAGE_ARTICLES, "News article pages"),
    ]

    title = models.CharField(max_length=200)
    advertiser_name = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to="media/adverts/%Y/%m/")
    target_url = models.URLField(max_length=1000, blank=True)
    display_type = models.CharField(max_length=20, choices=DISPLAY_CHOICES, default=DISPLAY_POPUP)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_DRAFT)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default=FREQUENCY_24_HOURS)
    page_target = models.CharField(max_length=20, choices=PAGE_CHOICES, default=PAGE_ALL)
    delay_seconds = models.PositiveSmallIntegerField(default=3, help_text="Seconds to wait before showing a popup (0–60).")
    priority = models.PositiveSmallIntegerField(default=100, help_text="Lower numbers are shown first when campaigns overlap.")
    created_by = models.ForeignKey(
        "newsapp.CustomUser", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="advertisement_campaigns"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["priority", "-created_at"]
        indexes = [
            models.Index(fields=["status", "start_at", "end_at"], name="newsapp_adv_status_3d2f9a_idx"),
            models.Index(fields=["display_type", "page_target"], name="newsapp_adv_display_3f0a71_idx"),
        ]

    def __str__(self):
        return self.title

    @property
    def is_in_schedule(self):
        now = timezone.now()
        return self.status == self.STATUS_ACTIVE and self.start_at <= now < self.end_at

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_at and self.end_at and self.end_at <= self.start_at:
            raise ValidationError({"end_at": "End date/time must be later than start date/time."})
        if self.delay_seconds is not None and not 0 <= self.delay_seconds <= 60:
            raise ValidationError({"delay_seconds": "Delay must be between 0 and 60 seconds."})

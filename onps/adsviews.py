from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST
from django.utils import timezone

from newsapp.forms import AdvertisementForm
from newsapp.models import Advertisement
from .adminviews import admin_only


@admin_only
def MANAGE_ADVERTISEMENTS(request):
    campaigns = Advertisement.objects.all()
    return render(request, "admin/manage_advertisements.html", {"campaigns": campaigns, "now": timezone.now()})


@admin_only
def ADD_ADVERTISEMENT(request):
    form = AdvertisementForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        advert = form.save(commit=False)
        advert.created_by = request.user
        advert.save()
        messages.success(request, "Advertisement campaign saved successfully.")
        return redirect("manage_advertisements")
    return render(request, "admin/advertisement_form.html", {"form": form, "page_title": "Create advertisement"})


@admin_only
def EDIT_ADVERTISEMENT(request, advert_id):
    advert = get_object_or_404(Advertisement, pk=advert_id)
    form = AdvertisementForm(request.POST or None, request.FILES or None, instance=advert)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Advertisement campaign updated successfully.")
        return redirect("manage_advertisements")
    return render(request, "admin/advertisement_form.html", {"form": form, "page_title": "Edit advertisement", "advert": advert})


@admin_only
@require_POST
def TOGGLE_ADVERTISEMENT(request, advert_id):
    advert = get_object_or_404(Advertisement, pk=advert_id)
    action = request.POST.get("action")
    if action == "pause":
        advert.status = Advertisement.STATUS_PAUSED
        message = "Advertisement campaign paused."
    elif action == "activate":
        advert.status = Advertisement.STATUS_ACTIVE
        message = "Advertisement campaign activated. It will display only within its scheduled dates."
    elif action == "draft":
        advert.status = Advertisement.STATUS_DRAFT
        message = "Advertisement campaign moved to draft."
    else:
        messages.error(request, "Invalid campaign action.")
        return redirect("manage_advertisements")
    advert.save(update_fields=["status", "updated_at"])
    messages.success(request, message)
    return redirect("manage_advertisements")


@admin_only
@require_POST
def DELETE_ADVERTISEMENT(request, advert_id):
    advert = get_object_or_404(Advertisement, pk=advert_id)
    advert.delete()
    messages.success(request, "Advertisement campaign deleted.")
    return redirect("manage_advertisements")

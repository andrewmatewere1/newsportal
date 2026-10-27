from .models import Category,Page

def category_processor(request):
    cat = Category.objects.all()
    return {'cat': cat}


def aboutus(request):
    first_page = Page.objects.first()
    return {'first_page':first_page}

def active_popup_advert(request):
    """Return the highest-priority scheduled popup for eligible public pages."""
    from django.utils import timezone
    from .models import Advertisement

    path = request.path.lower()
    if path.startswith(("/admin/", "/admin", "/login", "/dologin", "/dashboard")):
        return {"active_popup_advert": None}

    now = timezone.now()
    eligible = Advertisement.objects.filter(
        status=Advertisement.STATUS_ACTIVE,
        display_type=Advertisement.DISPLAY_POPUP,
        start_at__lte=now,
        end_at__gt=now,
    ).order_by("priority", "-created_at")

    if path == "/":
        advert = eligible.filter(page_target__in=[Advertisement.PAGE_ALL, Advertisement.PAGE_HOME]).first()
    elif "viewsinglenews" in path:
        advert = eligible.filter(page_target__in=[Advertisement.PAGE_ALL, Advertisement.PAGE_ARTICLES]).first()
    else:
        advert = eligible.filter(page_target=Advertisement.PAGE_ALL).first()
    return {"active_popup_advert": advert}


def social_links(request):
    """Expose all social icons, enabling links only for owner-configured HTTPS URLs."""
    from django.conf import settings

    links = [
        {"name": "Facebook", "url": settings.SOCIAL_FACEBOOK_URL, "icon": "ri-facebook-fill", "class": "social-facebook"},
        {"name": "X", "url": settings.SOCIAL_X_URL, "icon": "ri-twitter-x-fill", "class": "social-x"},
        {"name": "Instagram", "url": settings.SOCIAL_INSTAGRAM_URL, "icon": "ri-instagram-fill", "class": "social-instagram"},
        {"name": "WhatsApp", "url": settings.SOCIAL_WHATSAPP_URL, "icon": "ri-whatsapp-fill", "class": "social-whatsapp"},
    ]
    # Only HTTPS destinations are clickable. Blank or malformed values remain visible
    # as disabled icons until the publisher configures the real account/contact URL.
    for link in links:
        url = (link["url"] or "").strip()
        link["url"] = url if url.lower().startswith("https://") else ""
        link["configured"] = bool(link["url"])
    return {"social_links": links}

from django.test import TestCase, override_settings
from django.urls import reverse
from newsapp.models import CustomUser


class PublicPagesTests(TestCase):
    def test_homepage_is_public(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)

    @override_settings(STORAGES={
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
    })
    def test_dashboard_renders_for_user_without_profile_picture(self):
        user = CustomUser.objects.create_user(
            username="admin_without_picture",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.get(reverse("dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "assets/img/profile-img.jpg")

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse("dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn("/Login", response.url)


class RoleAccessTests(TestCase):
    def setUp(self):
        self.subadmin = CustomUser.objects.create_user(
            username="subadmin_test",
            email="subadmin@example.test",
            password="A-strong-test-password-42!",
            user_type="2",
        )

    def test_subadmin_cannot_manage_other_subadmins(self):
        self.client.force_login(self.subadmin)
        response = self.client.get(reverse("manage_subadmin"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_delete_endpoint_rejects_get(self):
        self.client.force_login(self.subadmin)
        response = self.client.get(reverse("delete_category", args=[999]))
        self.assertEqual(response.status_code, 405)


class AdvertisementManagementTests(TestCase):
    def setUp(self):
        self.admin = CustomUser.objects.create_user(
            username="primary_admin_test",
            email="primary-admin@example.test",
            password="A-strong-test-password-42!",
            user_type="1",
        )
        self.subadmin = CustomUser.objects.create_user(
            username="advert_subadmin_test",
            email="advert-subadmin@example.test",
            password="A-strong-test-password-43!",
            user_type="2",
        )

    def test_advertisement_management_requires_primary_admin(self):
        self.client.force_login(self.subadmin)
        response = self.client.get(reverse("manage_advertisements"))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse("dashboard"))

    def test_primary_admin_can_open_advertisement_manager(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse("manage_advertisements"))
        self.assertEqual(response.status_code, 200)

    def test_campaign_duration_form_calculates_24_hours(self):
        import base64
        from datetime import timedelta
        from django.utils import timezone
        from django.core.files.uploadedfile import SimpleUploadedFile
        from newsapp.forms import AdvertisementForm

        start = timezone.localtime().replace(second=0, microsecond=0)
        form = AdvertisementForm(data={
            "title": "24-hour test advert",
            "advertiser_name": "Test advertiser",
            "target_url": "",
            "display_type": "popup",
            "status": "draft",
            "start_at": start.strftime("%Y-%m-%dT%H:%M"),
            "end_at": "",
            "duration_preset": "24h",
            "frequency": "24h",
            "page_target": "all",
            "delay_seconds": "0",
            "priority": "100",
        }, files={"image": SimpleUploadedFile(
            "advert.png",
            base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4//8/AAX+Av4N70a4AAAAAElFTkSuQmCC"),
            content_type="image/png",
        )})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.cleaned_data["end_at"] - form.cleaned_data["start_at"], timedelta(hours=24))


class AdvertisementPublicDisplayTests(TestCase):
    def setUp(self):
        from datetime import timedelta
        from django.core.files.uploadedfile import SimpleUploadedFile
        from django.utils import timezone
        import base64
        from newsapp.models import Advertisement, Category, Subcategory, News

        self.now = timezone.now()
        self.advert = Advertisement.objects.create(
            title="Public test advert",
            advertiser_name="Test sponsor",
            image=SimpleUploadedFile(
                "advert.png",
                base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAIAAACQd1PeAAAADElEQVR4nGP4//8/AAX+Av4N70a4AAAAAElFTkSuQmCC"),
                content_type="image/png",
            ),
            target_url="https://example.test/",
            display_type=Advertisement.DISPLAY_POPUP,
            status=Advertisement.STATUS_ACTIVE,
            start_at=self.now - timedelta(hours=1),
            end_at=self.now + timedelta(hours=1),
            frequency=Advertisement.FREQUENCY_24_HOURS,
            page_target=Advertisement.PAGE_HOME,
            delay_seconds=0,
        )

    def test_active_homepage_campaign_is_rendered(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="news-advert-popup"')
        self.assertContains(response, "Public test advert")

    def test_paused_campaign_is_not_rendered(self):
        self.advert.status = "paused"
        self.advert.save(update_fields=["status"])
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="news-advert-popup"')

    def test_expired_campaign_is_not_rendered(self):
        from datetime import timedelta
        from django.utils import timezone
        self.advert.end_at = timezone.now() - timedelta(minutes=1)
        self.advert.save(update_fields=["end_at"])
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'id="news-advert-popup"')


@override_settings(STORAGES={
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
})
class SocialQuickLinksTests(TestCase):
    def test_homepage_shows_all_four_icons_when_destinations_are_unconfigured(self):
        from django.test import override_settings
        with override_settings(
            SOCIAL_FACEBOOK_URL="",
            SOCIAL_X_URL="",
            SOCIAL_INSTAGRAM_URL="",
            SOCIAL_WHATSAPP_URL="",
        ):
            response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        for platform, icon in [
            ("facebook", "ri-facebook-fill"),
            ("x", "ri-twitter-x-fill"),
            ("instagram", "ri-instagram-fill"),
            ("whatsapp", "ri-whatsapp-fill"),
        ]:
            self.assertContains(response, f'data-social-platform="{platform}"')
            self.assertContains(response, icon)
        self.assertContains(response, 'aria-disabled="true"')

    def test_configured_social_destinations_render_as_safe_external_links(self):
        from django.test import override_settings
        with override_settings(
            SOCIAL_FACEBOOK_URL="https://facebook.com/example-publisher",
            SOCIAL_X_URL="https://x.com/example-publisher",
            SOCIAL_INSTAGRAM_URL="https://instagram.com/example-publisher",
            SOCIAL_WHATSAPP_URL="https://wa.me/15551234567",
        ):
            response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        for url in [
            "https://facebook.com/example-publisher",
            "https://x.com/example-publisher",
            "https://instagram.com/example-publisher",
            "https://wa.me/15551234567",
        ]:
            self.assertContains(response, url)
        self.assertContains(response, 'target="_blank" rel="noopener noreferrer"')
        self.assertNotContains(response, 'aria-disabled="true"')

    def test_non_https_social_destinations_are_not_clickable(self):
        from django.test import override_settings
        with override_settings(
            SOCIAL_FACEBOOK_URL="javascript:alert(1)",
            SOCIAL_X_URL="http://x.com/example-publisher",
            SOCIAL_INSTAGRAM_URL="",
            SOCIAL_WHATSAPP_URL="",
        ):
            response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'href="javascript:alert(1)"')
        self.assertNotContains(response, 'href="http://x.com/example-publisher"')
        self.assertContains(response, 'data-social-platform="facebook"')
        self.assertContains(response, 'data-social-platform="x"')

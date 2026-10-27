# Advertisement campaigns

## Features
- Primary administrator-only campaign manager in the custom admin portal.
- Popup advert image, optional advertiser name, optional click-through URL. The popup include is integrated into `base1.html`, which is the shared public-site layout used by the homepage, article, category, search, about, and contact pages.
- Campaign states: Draft, Active, Paused.
- Scheduling uses start and end date/time. Presets calculate an end time 24 hours, 7 days, or 30 days after the selected start; Custom accepts an exact end date/time.
- Frequency choices: once per browser session, once every 24 hours per browser, or every eligible page visit.
- Page targeting: homepage, news article pages, or all public pages.
- Popup delay (0–60 seconds), campaign priority, edit, pause/resume, and delete.
- Expired campaigns stop displaying automatically because the public-site query requires `start_at <= now < end_at`.

## Apply changes
1. Back up the database and media files.
2. Install the project's dependencies from `requirements.txt`.
3. From the directory containing `manage.py`, run:
   `python manage.py migrate`
4. Run:
   `python manage.py check`
5. Run the test suite:
   `python manage.py test newsapp`
6. Log in to the existing primary administrator account and open **Advertisements** in the admin sidebar.
7. Create a campaign, upload an image, select start date/time and duration, set status to Active when ready, and save.

## Production notes
- Browser frequency controls are stored in sessionStorage/localStorage and therefore apply per browser profile, not to a verified person across devices.
- The ad's end time is exclusive: it stops displaying at the configured end time.
- Uploaded ad images use `media/adverts/YYYY/MM/` so they live under the existing `MEDIA_ROOT` layout and the Render persistent disk mounted at `/opt/render/project/src/media`. In production, verify that `MEDIA_ROOT` points at the persistent disk or configure object storage.
- The campaign status should be Active for the ad to display. Active campaigns are still hidden before their start time and after their end time.
- The custom portal views are restricted to the primary administrator (`user_type='1'`); subadministrators cannot manage advertising campaigns by default.


## Integration and validation
- The primary-admin sidebar includes an **Advertisements** entry.
- Public popup rendering is supplied by `newsapp.context_processors.active_popup_advert` and `templates/includes1/ad_popup.html`; the shared public layout includes this component.
- Uploaded advertisement images are limited to 5 MB by the form. Django's `ImageField` validates that the upload is a readable image.
- Run `python manage.py test newsapp` after installing dependencies. The added tests cover public display, paused campaigns, and expired campaigns.

# News Portal upgrade — implementation and verification report

## Implemented in this pass
- Preserved the existing Django project, custom `CustomUser` model, admin/subadmin roles, URLs, templates, article/category models, existing advertisement model, migrations, and media assets.
- Added/verified configurable homepage social quick links for Facebook, X, Instagram, and WhatsApp in the existing public-site footer (included on the homepage through `base1.html`). Uses the existing local Remix Icon library, including the X logo, with responsive styling, accessible labels/tooltips, hover/focus states, and safe new-tab attributes.
- All four icons now remain visible when configuration values are blank; unconfigured icons are visibly disabled rather than hidden or linked to invented destinations. Only HTTPS destinations are clickable.
- Registered/updated the social-links context processor and documented the four environment variables and valid WhatsApp link formats in `.env.example` and `DEPLOYMENT.md`.
- Added regression tests for all four icons, configured destinations, safe external-link attributes, and rejection of non-HTTPS destinations.
- Added `mysqlclient` to dependencies because the project explicitly supports environment-configured MySQL and includes a MySQL export.
- Documented advertisement administration, safe database backups, deployment and social-link configuration.

## Existing advertisement implementation inspected
The project already contains an `Advertisement` model and migrations, a `ModelForm`, administration templates, URL routes, scheduling logic, and a primary-admin-only decorator. These were retained rather than duplicated. Management uses `admin_only`, which checks the existing `user_type == '1'` role; status-changing and deletion actions are POST-only.

## Verification
- Python syntax compilation (`compileall`): passed.
- Django `check`: not run successfully because Django is not installed in this execution environment (`ModuleNotFoundError: No module named 'django'`).
- Migration consistency (`makemigrations --check --dry-run`): not run for the same missing dependency.
- Django automated tests: not run because Django is not installed in the execution environment. New social-link regression tests are present but remain unexecuted.
- Browser/device visual testing: not performed; responsive behavior is covered by CSS breakpoints but needs confirmation in a running browser.
- Browser/device, database connection, migration application, static collection, and deployment acceptance tests: not performed here.

## Before production deployment
1. Install dependencies with `pip install -r requirements.txt` in a clean environment.
2. Set `SECRET_KEY`, `DEBUG=False`, exact `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, and a production `DATABASE_URL` (or the documented MySQL variables).
3. Configure actual social URLs; do not use the example/test URLs from automated tests.
4. Back up and test-restore the existing database before importing the supplied SQL dump or applying migrations.
5. Run `python manage.py check --deploy`, `python manage.py makemigrations --check --dry-run`, `python manage.py migrate`, `python manage.py collectstatic --no-input`, and `python manage.py test`.
6. Confirm persistent media storage and test the public pages and admin/subadmin roles on the actual hosting provider.

## Files changed
- `newsapp/context_processors.py` — exposes four icon entries and permits clickable HTTPS destinations only.
- `onps/settings.py` — registers the context processor and reads social URL environment variables.
- `templates/includes1/footer.html` — renders the accessible social quick-link section.
- `static/assets1/css/style.css` — responsive styling and focus/hover states.
- `.env.example` — documents the four optional social URL variables.
- `newsapp/tests.py` — regression coverage for all four icons, configured links, and URL safety.
- `requirements.txt` — adds the MySQL database driver.
- `DEPLOYMENT.md` — social configuration, ad management, and database backup guidance.
- `IMPLEMENTATION_REPORT.md` — implementation and test status.

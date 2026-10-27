# Production preparation changes

## Configuration and deployment
- Removed the hard-coded Django secret key and made production require `SECRET_KEY`.
- `DEBUG` defaults to false; local development can set it in `.env`.
- Added environment-driven `ALLOWED_HOSTS`, CSRF trusted origins, PostgreSQL `DATABASE_URL`, optional environment-driven MySQL configuration, email settings, and HTTPS/security-cookie settings.
- Added WhiteNoise static-file serving and a dedicated `staticfiles/` collection directory.
- Restricted Django's development media-serving route to `DEBUG=True`.
- Added dependency manifest, `.env.example`, `.gitignore`, `build.sh`, `Procfile`, Render Blueprint, and deployment guide.
- Added optional S3-compatible media storage support and configured the Render Blueprint with a persistent media disk.

## Application hardening
- Added login protection to previously unprotected management views.
- Restricted primary-administrator-only tasks such as managing subadministrator accounts and editing global website settings.
- Converted destructive delete actions to CSRF-protected POST forms and POST-only endpoints.
- Added comment field length/required-field validation and a moderation status for new comments.
- Validated comment moderation status server-side.
- Added password validation when creating subadministrator accounts and changing passwords.
- Restricted public news listings/search/article pages to articles marked `Active`.
- Added basic automated tests for public access, dashboard authentication, role restrictions, and GET rejection on a delete endpoint.

## Data and release cautions
- The supplied SQLite database file was empty (0 bytes), so it was removed from the cleaned copy; local SQLite will be created by migrations.
- The project contains a separate historical MySQL SQL dump. It is retained in the archive but should not be pushed to a public repository or imported directly into production without reviewing and testing it.
- Existing media files are retained in the archive but excluded from Git. Copy them to the configured persistent disk or object storage after deployment if existing article images must remain available.
- Static Python syntax, YAML parsing, authentication-decorator coverage, and CSRF-token presence in POST forms were checked. Django runtime checks and browser-based acceptance tests still need to be run in an installed Django environment before public launch.

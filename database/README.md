# Database exports

The historical MariaDB/MySQL export is intentionally not included in this deployment ZIP because it may contain user/account records and is not directly importable into PostgreSQL. The Render test deployment creates a fresh PostgreSQL database and runs Django migrations. If you need to migrate historical records, keep the original SQL dump private and plan a separate, tested data migration.

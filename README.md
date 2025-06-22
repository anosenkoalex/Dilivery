# Dilivery

Demo CRM for courier deliveries.

## Setup

```bash
pip install -r requirements.txt
flask db upgrade
python app.py
```

Demo data are no longer generated automatically. Create your own zones, couriers and orders manually. Configuration values can be changed in `config.py` or via environment variables.

The app reads the database connection string from the `DATABASE_URL` environment variable. If the URL uses the legacy `postgres://` scheme it will be converted to `postgresql://` as required by SQLAlchemy.

If you are upgrading from previous versions remove the old SQLite database so that the new
`ImportJob` id format is applied:

```bash
rm Dilivery/database.db
# or in Windows PowerShell
del Dilivery\database.db
```

The application uses OpenStreetMap Nominatim for geocoding. Requests are limited to one per second.

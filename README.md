# Dilivery

Demo CRM for courier deliveries.

## Setup

```bash
pip install -r requirements.txt
flask db upgrade
python app.py
```

Demo data are no longer generated automatically. Create your own zones, couriers and orders manually. Configuration values can be changed in `config.py` or via environment variables.

The application expects the connection string in the
`SQLALCHEMY_DATABASE_URI` environment variable. `DATABASE_URL` is also
honoured for compatibility. Legacy `postgres://` URLs are automatically
converted to `postgresql+psycopg2://` which is required by SQLAlchemy.

If you are upgrading from previous versions remove the old SQLite database so that the new
`ImportJob` id format is applied:

```bash
rm Dilivery/database.db
# or in Windows PowerShell
del Dilivery\database.db
```

The application uses OpenStreetMap Nominatim for geocoding. Requests are limited to one per second.

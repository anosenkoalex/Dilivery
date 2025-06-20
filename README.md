# Dilivery

Demo CRM for courier deliveries.

## Setup

```bash
pip install -r requirements.txt
flask db upgrade
python app.py
```

On first start demo data will be generated automatically. Configuration values can be changed in `config.py` or via environment variables.

If you are upgrading from previous versions remove the old SQLite database so that the new
`ImportJob` id format is applied:

```bash
rm Dilivery/database.db
# or in Windows PowerShell
del Dilivery\database.db
```

The application uses OpenStreetMap Nominatim for geocoding. Requests are limited to one per second.

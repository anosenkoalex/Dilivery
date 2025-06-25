from app import app, db
from flask_migrate import Migrate, upgrade, migrate

migrate_obj = Migrate(app, db)

with app.app_context():
    migrate(message="Add import_batch_id and import_batch_label to orders")
    upgrade()

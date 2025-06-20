from datetime import datetime
from uuid import uuid4

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.dialects.postgresql import UUID


db = SQLAlchemy()


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(64), nullable=False)
    client_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(64))
    address = db.Column(db.String(256))
    note = db.Column(db.Text)
    import_batch = db.Column(db.String(64))
    status = db.Column(db.String(64), default="Складская обработка")
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    zone = db.Column(db.String(64))
    delivered_at = db.Column(db.Date)
    comment = db.Column(db.Text)
    problem_comment = db.Column(db.Text)
    photo_filename = db.Column(db.String(128))
    courier_id = db.Column(db.Integer, db.ForeignKey("couriers.id"))
    courier = db.relationship("Courier", backref="orders")


class DeliveryZone(db.Model):
    __tablename__ = "zones"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    color = db.Column(db.String(32), default="#3388ff")
    polygon_json = db.Column(db.Text, nullable=False)


class Courier(db.Model):
    __tablename__ = "couriers"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    telegram = db.Column(db.String(64))
    zones = db.Column(db.String(256))


class User(db.Model, UserMixin):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(512), nullable=False)
    role = db.Column(db.String(16), nullable=False)


class ImportJob(db.Model):
    __tablename__ = "import_jobs"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    filename = db.Column(db.String(256))
    total_rows = db.Column(db.Integer)
    processed_rows = db.Column(db.Integer, default=0)
    status = db.Column(db.String(32), default="running")
    started_at = db.Column(db.DateTime, default=datetime.utcnow)
    finished_at = db.Column(db.DateTime)

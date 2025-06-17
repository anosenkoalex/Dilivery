from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Order(db.Model):
    __tablename__ = "orders"
    id = db.Column(db.Integer, primary_key=True)
    order_number = db.Column(db.String(64), nullable=False)
    client_name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(64))
    address = db.Column(db.String(256))
    note = db.Column(db.Text)
    status = db.Column(db.String(64), default="Складская обработка")
    latitude = db.Column(db.Float)
    longitude = db.Column(db.Float)
    zone = db.Column(db.String(64))


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

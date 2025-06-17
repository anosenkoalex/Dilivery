import json
from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Order, DeliveryZone, Courier
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'secret'

db.init_app(app)


def point_in_polygon(x, y, polygon):
    inside = False
    n = len(polygon)
    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def detect_zone(lat, lng):
    zones = DeliveryZone.query.all()
    for zone in zones:
        polygon = json.loads(zone.polygon_json)
        if point_in_polygon(lng, lat, polygon):
            return zone.name
    return None


def init_demo_data():
    if Order.query.first():
        return
    # create demo zones
    zone1 = DeliveryZone(name='Zone A', color='#ff0000', polygon_json=json.dumps([[37.6, 55.7], [37.7, 55.7], [37.7, 55.8], [37.6, 55.8]]))
    zone2 = DeliveryZone(name='Zone B', color='#00ff00', polygon_json=json.dumps([[37.7, 55.7], [37.8, 55.7], [37.8, 55.8], [37.7, 55.8]]))
    db.session.add_all([zone1, zone2])
    db.session.commit()
    # create orders
    orders = [
        Order(order_number='1001', client_name='Иван Иванов', phone='+70000000001', address='Москва', status='Складская обработка', latitude=55.75, longitude=37.65),
        Order(order_number='1002', client_name='Петр Петров', phone='+70000000002', address='Москва', status='Складская обработка', latitude=55.75, longitude=37.75),
        Order(order_number='1003', client_name='Сергей Сергеев', phone='+70000000003', address='Москва', status='Складская обработка'),
    ]
    for o in orders:
        if o.latitude and o.longitude:
            zone = detect_zone(o.latitude, o.longitude)
            o.zone = zone
        db.session.add(o)
    db.session.commit()
    couriers = [
        Courier(name='Курьер 1', telegram='@courier1', zones='Zone A'),
        Courier(name='Курьер 2', telegram='@courier2', zones='Zone B'),
    ]
    db.session.add_all(couriers)
    db.session.commit()

with app.app_context():
    db.create_all()
    init_demo_data()


def login_required(func):
    from functools import wraps

    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user' not in session:
            return redirect(url_for('login'))
        return func(*args, **kwargs)

    return wrapper


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == 'password':
            session['user'] = 'admin'
            return redirect(url_for('orders'))
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


@app.route('/orders', methods=['GET', 'POST'])
@login_required
def orders():
    if request.method == 'POST':
        order_id = request.form['id']
        status = request.form['status']
        order = Order.query.get(order_id)
        if order:
            order.status = status
            db.session.commit()
    orders = Order.query.all()
    return render_template('orders.html', orders=orders)


@app.route('/map')
@login_required
def map_view():
    orders = Order.query.all()
    zones = DeliveryZone.query.all()
    return render_template('map.html', orders=orders, zones=zones)


@app.route('/zones')
@login_required
def zones():
    zones = DeliveryZone.query.all()
    return render_template('zones.html', zones=zones)


@app.route('/couriers')
@login_required
def couriers():
    couriers = Courier.query.all()
    return render_template('couriers.html', couriers=couriers)


if __name__ == '__main__':
    app.run(debug=True)

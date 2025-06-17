import json
import csv
import uuid
import os
from flask import Flask, render_template, request, redirect, url_for, session, flash
from models import db, Order, DeliveryZone, Courier
import openpyxl

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


def geocode(address):
    """Placeholder geocoder returning None coordinates."""
    return None, None


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
        Order(order_number='1001', client_name='Иван Иванов', phone='+70000000001', address='Москва', status='Складская обработка', latitude=55.75, longitude=37.65, note=''),
        Order(order_number='1002', client_name='Петр Петров', phone='+70000000002', address='Москва', status='Складская обработка', latitude=55.75, longitude=37.75, note=''),
        Order(order_number='1003', client_name='Сергей Сергеев', phone='+70000000003', address='Москва', status='Складская обработка', note=''),
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


@app.route('/orders/<int:order_id>/update', methods=['POST'])
@login_required
def update_order(order_id):
    order = Order.query.get_or_404(order_id)
    old_address = order.address
    order.client_name = request.form.get('client_name', order.client_name)
    order.phone = request.form.get('phone', order.phone)
    order.address = request.form.get('address', order.address)
    order.note = request.form.get('note', order.note)
    if order.address != old_address:
        lat, lng = geocode(order.address)
        order.latitude = lat
        order.longitude = lng
        if lat and lng:
            order.zone = detect_zone(lat, lng)
        else:
            order.zone = None
            flash('Не удалось определить координаты по адресу', 'warning')
    db.session.commit()
    flash('Заказ обновлен', 'success')
    return redirect(url_for('orders'))

@app.route('/orders/<int:order_id>/set_coords', methods=['GET', 'POST'])
@login_required
def set_coords(order_id):
    order = Order.query.get_or_404(order_id)
    if request.method == 'POST':
        lat = request.form.get('latitude')
        lng = request.form.get('longitude')
        try:
            lat = float(lat)
            lng = float(lng)
        except (TypeError, ValueError):
            flash('Некорректные координаты', 'warning')
            return redirect(url_for('set_coords', order_id=order_id))
        order.latitude = lat
        order.longitude = lng
        order.zone = detect_zone(lat, lng)
        db.session.commit()
        flash('Координаты сохранены', 'success')
        return redirect(url_for('orders'))
    return render_template('set_coords.html', order=order)


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


def read_file_rows(path):
    if path.lower().endswith('.csv'):
        with open(path, newline='', encoding='utf-8-sig') as f:
            return [row for row in csv.reader(f)]
    wb = openpyxl.load_workbook(path, read_only=True)
    sheet = wb.active
    rows = []
    for r in sheet.iter_rows(values_only=True):
        rows.append([str(c) if c is not None else '' for c in r])
    return rows


@app.route('/orders/import', methods=['GET', 'POST'])
@login_required
def import_orders():
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            return redirect(url_for('import_orders'))
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.csv', '.xlsx']:
            return redirect(url_for('import_orders'))
        uid = str(uuid.uuid4()) + ext
        upload_dir = os.path.join(app.root_path, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        path = os.path.join(upload_dir, uid)
        file.save(path)
        rows = read_file_rows(path)
        first = rows[0] if rows else []
        columns = [{'index': i, 'name': v or f"Column {i+1}"} for i, v in enumerate(first)]
        return render_template('import_mapping.html', file_id=uid, columns=columns, header=True)
    return render_template('import_upload.html')


@app.route('/orders/import/finish', methods=['POST'])
@login_required
def import_orders_finish():
    file_id = request.form.get('file_id')
    if not file_id:
        return redirect(url_for('import_orders'))
    path = os.path.join(app.root_path, 'uploads', file_id)
    if not os.path.exists(path):
        return redirect(url_for('import_orders'))
    header = request.form.get('header') == 'on'
    mapping = {}
    for field in ['order_number', 'client_name', 'phone', 'address']:
        val = request.form.get(field)
        mapping[field] = int(val) if val and val.isdigit() else None
    rows = read_file_rows(path)
    if header:
        rows = rows[1:]
    counter = Order.query.count() + 1

    def gen_order():
        nonlocal counter
        num = f"ORD{counter:03d}"
        counter += 1
        return num

    imported = 0
    for r in rows:
        client_idx = mapping['client_name']
        addr_idx = mapping['address']
        if client_idx is None or addr_idx is None:
            break
        if client_idx >= len(r) or addr_idx >= len(r):
            continue
        client_name = str(r[client_idx]).strip()
        address = str(r[addr_idx]).strip()
        if not client_name or not address:
            continue
        if mapping['order_number'] is not None and mapping['order_number'] < len(r):
            onum = str(r[mapping['order_number']]).strip()
        else:
            onum = ''
        order_number = onum if onum else gen_order()
        phone = ''
        if mapping['phone'] is not None and mapping['phone'] < len(r):
            phone = str(r[mapping['phone']]).strip()
        lat, lng = geocode(address)
        zone = detect_zone(lat, lng) if lat and lng else None
        order = Order(order_number=order_number,
                      client_name=client_name,
                      phone=phone,
                      address=address,
                      latitude=lat,
                      longitude=lng,
                      zone=zone)
        db.session.add(order)
        imported += 1
    db.session.commit()
    os.remove(path)
    return render_template('import_result.html', count=imported)


if __name__ == '__main__':
    app.run(debug=True)

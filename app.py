import json
import csv
import uuid
import os
import time
from datetime import date, timedelta
from flask import Flask, render_template, request, redirect, url_for, flash, send_file, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, Order, DeliveryZone, Courier, User
from config import Config
from sqlalchemy import func
import openpyxl
from io import BytesIO
from geocode import geocode_address

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def admin_required(func):
    from functools import wraps

    @wraps(func)
    @login_required
    def wrapper(*args, **kwargs):
        if current_user.role != 'admin':
            return redirect(url_for('orders'))
        return func(*args, **kwargs)

    return wrapper


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


def assign_courier_for_zone(zone_name):
    """Return Courier instance serving the given zone name."""
    if not zone_name:
        return None
    couriers = Courier.query.all()
    for c in couriers:
        if c.zones:
            zones = [z.strip() for z in c.zones.split(',') if z.strip()]
            if zone_name in zones:
                return c
    return None

def populate_demo_data():
    """Populate database with demo zones, couriers and orders."""
    if Order.query.first():
        return

    zones = []
    for i in range(5):
        polygon = [
            [37.6 + i * 0.05, 55.7],
            [37.65 + i * 0.05, 55.7],
            [37.65 + i * 0.05, 55.75],
            [37.6 + i * 0.05, 55.75],
        ]
        zone = DeliveryZone(
            name=f"Zone {i + 1}",
            color=f"#33{i}{i}ff" if i < 10 else "#3388ff",
            polygon_json=json.dumps(polygon),
        )
        zones.append(zone)
    db.session.add_all(zones)
    db.session.commit()

    couriers = []
    users = [User(username="admin", password_hash=generate_password_hash("admin"), role="admin")]
    for i in range(5):
        courier = Courier(name=f"Courier {i+1}", telegram=f"@courier{i+1}", zones=f"Zone {i+1}")
        couriers.append(courier)
        users.append(User(username=f"courier{i+1}", password_hash=generate_password_hash("courier"), role="courier"))
    db.session.add_all(couriers)
    db.session.add_all(users)
    db.session.commit()

    orders = []
    for i in range(20):
        zone = zones[i % 5]
        lat = 55.71 + (i % 5) * 0.01
        lng = 37.61 + (i % 5) * 0.01
        order = Order(
            order_number=f"ORD{100 + i}",
            client_name=f"Client {i+1}",
            phone=f"+700000000{(i+1):02d}",
            address=f"Demo address {i+1}",
            latitude=lat,
            longitude=lng,
            zone=zone.name,
            courier=couriers[i % 5],
        )
        orders.append(order)
    db.session.add_all(orders)
    db.session.commit()

with app.app_context():
    db.create_all()
    populate_demo_data()


@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('orders'))
    else:
        return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Вы вошли в систему', 'success')
            return redirect(url_for('orders'))
        flash('Неверные логин или пароль', 'warning')
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы', 'success')
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
            if status == 'Доставлен':
                order.delivered_at = date.today()
            else:
                order.delivered_at = None
            db.session.commit()
            flash('Статус заказа обновлён', 'success')
        return redirect(url_for('orders'))
    query = Order.query
    if current_user.role == 'courier':
        courier = Courier.query.filter_by(telegram=f'@{current_user.username}').first()
        zones = []
        if courier and courier.zones:
            zones = [z.strip() for z in courier.zones.split(',') if z.strip()]
        if zones:
            query = query.filter(Order.zone.in_(zones))
        else:
            query = query.filter(db.text('0=1'))
    orders = query.all()
    orders_by_zone = {}
    for o in orders:
        key = o.zone or 'Не определена'
        orders_by_zone.setdefault(key, []).append(o)
    couriers_list = Courier.query.all()
    return render_template('orders.html', orders=orders, orders_by_zone=orders_by_zone, couriers=couriers_list)


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
        lat, lng = geocode_address(order.address)
        order.latitude = lat
        order.longitude = lng
        if lat and lng:
            order.zone = detect_zone(lat, lng)
        else:
            order.zone = None
            flash('Не удалось определить координаты по адресу', 'warning')
    courier_val = request.form.get('courier_id')
    if courier_val:
        try:
            order.courier_id = int(courier_val)
        except ValueError:
            order.courier_id = None
    elif order.zone:
        c = assign_courier_for_zone(order.zone)
        order.courier = c
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
        c = assign_courier_for_zone(order.zone)
        order.courier = c
        db.session.commit()
        flash('Координаты сохранены', 'success')
        return redirect(url_for('orders'))
    return render_template('set_coords.html', order=order)


@app.route('/orders/set_point', methods=['POST'])
@login_required
def set_point():
    order_id = request.form.get('order_id')
    lat = request.form.get('lat')
    lon = request.form.get('lon')
    try:
        order_id = int(order_id)
        lat = float(lat)
        lon = float(lon)
    except (TypeError, ValueError):
        return jsonify({'success': False}), 400
    order = Order.query.get_or_404(order_id)
    order.latitude = lat
    order.longitude = lon
    order.zone = detect_zone(lat, lon)
    c = assign_courier_for_zone(order.zone)
    order.courier = c
    db.session.commit()
    return jsonify({'success': True, 'zone': order.zone})


@app.route('/orders/<int:order_id>/add_comment_photo', methods=['POST'])
@login_required
def add_comment_photo(order_id):
    if current_user.role != 'courier':
        return redirect(url_for('orders'))
    order = Order.query.get_or_404(order_id)
    comment = request.form.get('comment', '').strip()
    file = request.files.get('photo')
    if file and file.filename:
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.jpg', '.jpeg', '.png']:
            flash('Допустимы только файлы JPG и PNG', 'warning')
            return redirect(url_for('orders'))
        upload_dir = os.path.join(app.static_folder, 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filename = f"order_{order_id}_{int(time.time())}.jpg"
        path = os.path.join(upload_dir, filename)
        file.save(path)
        order.photo_filename = filename
    if comment:
        order.comment = comment
    db.session.commit()
    flash('Комментарий сохранен', 'success')
    return redirect(url_for('orders'))


@app.route('/map')
@login_required
def map_view():
    query = Order.query
    if current_user.role == 'courier':
        courier = Courier.query.filter_by(telegram=f'@{current_user.username}').first()
        zones = []
        if courier and courier.zones:
            zones = [z.strip() for z in courier.zones.split(',') if z.strip()]
        if zones:
            query = query.filter(Order.zone.in_(zones))
        else:
            query = query.filter(db.text('0=1'))
    orders = query.all()
    orders_dict = [
        {
            "id": o.id,
            "address": o.address,
            "lat": o.latitude,
            "lng": o.longitude,
            "zone": o.zone,
            "status": o.status,
        }
        for o in orders
    ]

    zones = DeliveryZone.query.all()
    zones_dict = [
        {
            "id": z.id,
            "name": z.name,
            "color": z.color,
            "polygon": json.loads(z.polygon_json),
        }
        for z in zones
    ]

    return render_template("map.html", orders=orders_dict, zones=zones_dict)


@app.route('/zones')
@admin_required
def zones():
    zones = DeliveryZone.query.all()
    zones_dict = [
        {
            "id": z.id,
            "name": z.name,
            "color": z.color,
            "polygon": json.loads(z.polygon_json),
        }
        for z in zones
    ]

    return render_template("zones.html", zones=zones_dict)


@app.route('/zones/<int:zone_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_zone(zone_id):
    zone = DeliveryZone.query.get_or_404(zone_id)
    if request.method == 'POST':
        zone.name = request.form.get('name', zone.name)
        zone.color = request.form.get('color', zone.color)
        polygon = request.form.get('polygon')
        if polygon:
            zone.polygon_json = polygon
        db.session.commit()
        flash('Зона обновлена', 'success')
        return redirect(url_for('zones'))
    return render_template('edit_zone.html', zone=zone)


@app.route('/zones/<int:zone_id>/delete')
@admin_required
def delete_zone(zone_id):
    zone = DeliveryZone.query.get_or_404(zone_id)
    Order.query.filter_by(zone=zone.name).update({'zone': None, 'courier_id': None})
    db.session.delete(zone)
    db.session.commit()
    flash('Зона удалена', 'success')
    return redirect(url_for('zones'))


@app.route('/couriers')
@admin_required
def couriers():
    couriers = Courier.query.all()
    return render_template('couriers.html', couriers=couriers)


@app.route('/users')
@admin_required
def users():
    all_users = User.query.all()
    data = []
    for u in all_users:
        zones = ''
        if u.role == 'courier':
            c = Courier.query.filter_by(telegram=f'@{u.username}').first()
            zones = c.zones if c and c.zones else ''
        data.append({'user': u, 'zones': zones})
    zones_list = DeliveryZone.query.all()
    return render_template('users.html', users=data, zones=zones_list)


@app.route('/users/create', methods=['POST'])
@admin_required
def create_user():
    username = request.form.get('username')
    password = request.form.get('password')
    zones = request.form.getlist('zones')
    if not username or not password:
        flash('Введите имя и пароль', 'warning')
        return redirect(url_for('users'))
    if User.query.filter_by(username=username).first():
        flash('Такой пользователь уже существует', 'warning')
        return redirect(url_for('users'))
    user = User(username=username, password_hash=generate_password_hash(password), role='courier')
    courier = Courier(name=username, telegram=f'@{username}', zones=', '.join(zones))
    db.session.add(user)
    db.session.add(courier)
    db.session.commit()
    flash('Курьер создан', 'success')
    return redirect(url_for('users'))


def _history_query(period):
    q = Order.query.filter_by(status='Доставлен')
    today = date.today()
    if period == 'today':
        start = today
    elif period == '7':
        start = today - timedelta(days=7)
    elif period == 'month':
        start = today - timedelta(days=30)
    else:
        start = None
    if start:
        q = q.filter(Order.delivered_at >= start)
    return q


@app.route('/history')
@admin_required
def history():
    period = request.args.get('period', 'today')
    orders = _history_query(period).all()
    return render_template('history.html', orders=orders, period=period)


@app.route('/history/export')
@admin_required
def export_history():
    period = request.args.get('period', 'today')
    orders = _history_query(period).all()

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['№ заказа', 'Имя', 'Телефон', 'Адрес', 'Дата', 'Зона'])
    for o in orders:
        dt = o.delivered_at.isoformat() if o.delivered_at else ''
        ws.append([o.order_number, o.client_name, o.phone, o.address, dt, o.zone or ''])

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    filename = f"dostavki_{date.today().isoformat()}.xlsx"
    return send_file(buf, as_attachment=True, download_name=filename,
                     mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


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
@admin_required
def import_orders():
    if request.method == 'POST' and 'file' in request.files:
        file = request.files['file']
        if file.filename == '':
            flash('Выберите файл', 'warning')
            return redirect(url_for('import_orders'))
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ['.csv', '.xlsx']:
            flash('Недопустимый формат файла', 'warning')
            return redirect(url_for('import_orders'))
        uid = str(uuid.uuid4()) + ext
        upload_dir = app.config['UPLOAD_FOLDER']
        os.makedirs(upload_dir, exist_ok=True)
        path = os.path.join(upload_dir, uid)
        file.save(path)
        rows = read_file_rows(path)
        first = rows[0] if rows else []
        columns = [{'index': i, 'name': v or f"Column {i+1}"} for i, v in enumerate(first)]
        return render_template('import_mapping.html', file_id=uid, columns=columns, header=True)
    return render_template('import_upload.html')


@app.route('/orders/import/finish', methods=['POST'])
@admin_required
def import_orders_finish():
    file_id = request.form.get('file_id')
    if not file_id:
        return redirect(url_for('import_orders'))

    path = os.path.join(app.config['UPLOAD_FOLDER'], file_id)
    if not os.path.exists(path):
        return redirect(url_for('import_orders'))

    header = request.form.get('header') == 'on'
    mapping = {}
    for field in ["order_number", "client_name", "phone", "address"]:
        value = request.form.get(field)
        mapping[field] = int(value) if value and value.isdigit() else None

    rows = read_file_rows(path)
    if header:
        rows = rows[1:]

    next_id = Order.query.count() + 1

    def next_order_number():
        nonlocal next_id
        num = f"ORD{next_id:03d}"
        next_id += 1
        return num

    imported = 0
    ni = mapping.get("order_number")
    ci = mapping.get("client_name")
    pi = mapping.get("phone")
    ai = mapping.get("address")

    for idx, row in enumerate(rows, 1):
        try:
            # отладочный лог
            print(f"[{idx}] Строка: {row}")

            if ci is None or ai is None:
                break
            if ci >= len(row) or ai >= len(row):
                continue

            client_name = str(row[ci]).strip()
            address = str(row[ai]).strip()
            if not client_name or not address:
                continue

            if ni is not None and ni < len(row):
                order_number = str(row[ni]).strip()
            else:
                order_number = ""
            order_number = order_number or next_order_number()

            phone = ""
            if pi is not None and pi < len(row):
                phone = str(row[pi]).strip()

            lat, lon = geocode_address(address)
            zone = detect_zone(lat, lon) if lat and lon else None
            order = Order(
                order_number=order_number,
                client_name=client_name,
                phone=phone,
                address=address,
                latitude=lat,
                longitude=lon,
                zone=zone,
            )

            if zone:
                courier = assign_courier_for_zone(zone)
                if courier:
                    order.courier = courier

            db.session.add(order)
            imported += 1
        except Exception as e:
            print(f"[!] Ошибка при импорте строки {idx}: {row}")
            print(f"    → {type(e).__name__}: {e}")

    print(f"[+] Импортировано строк: {imported} из {len(rows)}")

    db.session.commit()

    try:
        os.remove(path)
    except PermissionError:
        time.sleep(1)
        try:
            os.remove(path)
        except Exception as e:
            print(f"[!] Ошибка удаления файла: {e}")

    flash(f'Импортировано заказов: {imported}', 'success')
    return render_template('import_result.html', count=imported)


@app.route('/stats')
@admin_required
def stats():
    zones = DeliveryZone.query.all()
    couriers = Courier.query.all()
    return render_template('stats.html', zones=zones, couriers=couriers)


@app.route('/stats/data')
@admin_required
def stats_data():
    period = request.args.get('period', 'today')
    zone = request.args.get('zone')
    courier_id = request.args.get('courier')

    q = Order.query.filter_by(status='Доставлен')
    today = date.today()
    if period == 'today':
        start = today
    elif period == 'week':
        start = today - timedelta(days=7)
    elif period == 'month':
        start = today - timedelta(days=30)
    else:
        start = None
    if start:
        q = q.filter(Order.delivered_at >= start)
    if zone:
        q = q.filter(Order.zone == zone)
    if courier_id:
        courier = Courier.query.get(int(courier_id))
        if courier and courier.zones:
            zones = [z.strip() for z in courier.zones.split(',') if z.strip()]
            if zones:
                q = q.filter(Order.zone.in_(zones))

    daily = q.with_entities(Order.delivered_at, func.count()).group_by(Order.delivered_at).order_by(Order.delivered_at).all()
    zone_data = q.with_entities(Order.zone, func.count()).group_by(Order.zone).all()

    resp = {
        'dates': [d[0].isoformat() if d[0] else '' for d in daily],
        'counts': [d[1] for d in daily],
        'zone_labels': [z[0] or '—' for z in zone_data],
        'zone_counts': [z[1] for z in zone_data],
    }
    return jsonify(resp)


if __name__ == '__main__':
    app.run(debug=True)

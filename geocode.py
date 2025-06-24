import json
import requests
import time
from shapely.geometry import shape, Point

from models import WorkArea

_last_request_time = 0


def is_inside_work_area(lat, lon):
    area = WorkArea.query.first()
    if not area:
        return True
    try:
        poly = shape(json.loads(area.geojson)["geometry"])
        return poly.contains(Point(lon, lat))
    except Exception:
        return True


def _get_bbox():
    area = WorkArea.query.first()
    if not area:
        return None
    try:
        geom = shape(json.loads(area.geojson)["geometry"])
        minx, miny, maxx, maxy = geom.bounds
        # Nominatim expects left, top, right, bottom (lon/lat)
        return f"{minx},{maxy},{maxx},{miny}"
    except Exception:
        return None


def geocode_address(address: str):
    """Return latitude, longitude and a flag indicating inclusion in work area."""
    global _last_request_time
    if not address:
        return None, None, None
    # ensure no more than 1 request per second
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < 1:
        time.sleep(1 - elapsed)
    bbox = _get_bbox()
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
        "countrycodes": "kg",
    }
    if bbox:
        params["viewbox"] = bbox
        params["bounded"] = 1
    headers = {"User-Agent": "delivery_crm_app (bishkek only)"}
    try:
        resp = requests.get(
            "https://nominatim.openstreetmap.org/search",
            params=params,
            headers=headers,
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            if data:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                _last_request_time = time.time()
                inside = is_inside_work_area(lat, lon)
                return lat, lon, inside
    except Exception:
        pass
    _last_request_time = time.time()
    return None, None, None

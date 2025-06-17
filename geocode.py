import requests
import time

_last_request_time = 0


def geocode_address(address: str):
    """Return latitude and longitude for address using Nominatim."""
    global _last_request_time
    if not address:
        return None, None
    # ensure no more than 1 request per second
    now = time.time()
    elapsed = now - _last_request_time
    if elapsed < 1:
        time.sleep(1 - elapsed)
    params = {
        "q": address,
        "format": "json",
        "limit": 1,
    }
    headers = {"User-Agent": "delivery_crm_app"}
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
                return lat, lon
    except Exception:
        pass
    _last_request_time = time.time()
    return None, None

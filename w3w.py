import requests

def words_from_coordinates(lat, lon, api_key):
    if not api_key:
        return {"status": "not_requested"}
    url = "https://api.what3words.com/v3/convert-to-3wa"
    r = requests.get(url, params={
        "coordinates": f"{lat},{lon}",
        "key": api_key,
        "language": "en"
    }, timeout=15)
    r.raise_for_status()
    data = r.json()
    return {
        "words": data.get("words"),
        "map": data.get("map"),
        "language": data.get("language"),
        "status": "ok"
    }

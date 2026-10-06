import simplekml

def make_kml(records, output_path):
    kml = simplekml.Kml()
    for i, r in enumerate(records, 1):
        lat = r["derived"]["wgs84"]["latitude"]
        lon = r["derived"]["wgs84"]["longitude"]
        source = r.get("observation_type", "coordinate")
        p = kml.newpoint(
            name=f"Coordinate {i} ({source})",
            coords=[(lon, lat)]
        )
        p.description = (
            f"Observation type: {source}<br/>"
            f"Raw OCR: {r.get('raw_text')}<br/>"
            f"Format: {r.get('format')}<br/>"
            f"Confidence: {r.get('confidence')}<br/>"
            f"MGRS: {r['derived']['mgrs']}<br/>"
            f"Plus Code: {r['derived']['plus_code']}<br/>"
            f"Geohash: {r['derived']['geohash']}"
        )
    kml.save(str(output_path))

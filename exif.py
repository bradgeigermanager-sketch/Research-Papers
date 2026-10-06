"""EXIF metadata extraction and coordinate normalization.

EXIF GPS coordinates are treated as source observations. They are normalized
to WGS84 decimal latitude/longitude when possible, while preserving the
original EXIF values for provenance.
"""
from fractions import Fraction
from PIL import Image, ExifTags

GPS_TAGS = {
    v: k for k, v in ExifTags.GPSTAGS.items()
}

def _rational(value):
    if isinstance(value, tuple) and len(value) == 2:
        return float(value[0]) / float(value[1])
    if isinstance(value, Fraction):
        return float(value)
    try:
        return float(value)
    except Exception:
        return None

def _dms(values):
    if not values or len(values) < 3:
        return None
    parts = [_rational(v) for v in values[:3]]
    if any(v is None for v in parts):
        return None
    return parts[0] + parts[1] / 60.0 + parts[2] / 3600.0

def extract_exif(image_path):
    img = Image.open(image_path)
    exif = img.getexif()

    general = {}
    gps = {}

    for tag_id, value in exif.items():
        tag_name = ExifTags.TAGS.get(tag_id, str(tag_id))
        if tag_name == "GPSInfo":
            continue
        try:
            if isinstance(value, bytes):
                value = value.decode("utf-8", errors="replace")
            elif not isinstance(value, (str, int, float, list, tuple)):
                value = str(value)
        except Exception:
            value = str(value)
        general[tag_name] = value

    gps_ifd = {}
    try:
        raw_gps = exif.get_ifd(0x8825)  # GPS IFD
        for tag_id, value in raw_gps.items():
            gps_ifd[ExifTags.GPSTAGS.get(tag_id, str(tag_id))] = value
    except Exception:
        raw_gps = {}

    lat = _dms(gps_ifd.get("GPSLatitude"))
    lon = _dms(gps_ifd.get("GPSLongitude"))
    lat_ref = gps_ifd.get("GPSLatitudeRef")
    lon_ref = gps_ifd.get("GPSLongitudeRef")

    if isinstance(lat_ref, bytes):
        lat_ref = lat_ref.decode(errors="replace")
    if isinstance(lon_ref, bytes):
        lon_ref = lon_ref.decode(errors="replace")

    if lat is not None and str(lat_ref).upper().startswith("S"):
        lat = -lat
    if lon is not None and str(lon_ref).upper().startswith("W"):
        lon = -lon

    # Preserve serializable GPS metadata where practical.
    for k, v in gps_ifd.items():
        if isinstance(v, bytes):
            gps[k] = v.decode(errors="replace")
        elif isinstance(v, tuple):
            gps[k] = [str(x) for x in v]
        else:
            gps[k] = v

    result = {
        "metadata": general,
        "gps_exif": gps,
        "coordinate_observation": None,
    }

    if lat is not None and lon is not None and -90 <= lat <= 90 and -180 <= lon <= 180:
        result["coordinate_observation"] = {
            "latitude": lat,
            "longitude": lon,
            "datum": "WGS84",
            "source": "image_exif_gps",
            "source_fields": [
                "GPSLatitude", "GPSLatitudeRef",
                "GPSLongitude", "GPSLongitudeRef"
            ]
        }

    return result

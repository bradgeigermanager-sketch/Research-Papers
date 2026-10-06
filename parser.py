import re
import math
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict, Tuple

from pyproj import Geod
import mgrs
from openlocationcode import openlocationcode as olc

GEOD = Geod(ellps="WGS84")
MGRS = mgrs.MGRS()

@dataclass
class CoordinateCandidate:
    raw_text: str
    latitude: Optional[float]
    longitude: Optional[float]
    format: str
    confidence: float
    source: Dict

def dms_to_decimal(deg, minutes=0, seconds=0, hemisphere=None):
    value = abs(float(deg)) + abs(float(minutes))/60 + abs(float(seconds))/3600
    if hemisphere and hemisphere.upper() in ("S", "W"):
        value = -value
    elif float(deg) < 0:
        value = -value
    return value

def decimal_to_dms(value, positive="N", negative="S"):
    hemi = positive if value >= 0 else negative
    x = abs(value)
    d = int(x)
    m_float = (x-d)*60
    m = int(m_float)
    s = (m_float-m)*60
    return d, m, s, hemi

def normalize_pair(lat, lon, fmt, raw, source, confidence=0.95):
    lat, lon = float(lat), float(lon)
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return CoordinateCandidate(raw, lat, lon, fmt, confidence, source)

def parse_decimal(text, source):
    # Explicit lat/lon labels
    p = re.compile(
        r'(?i)(?:lat(?:itude)?\s*[:=]?\s*)?'
        r'([+-]?\d{1,3}(?:\.\d+)?)\s*[,;/ ]+\s*'
        r'(?:lon(?:gitude)?\s*[:=]?\s*)?'
        r'([+-]?\d{1,3}(?:\.\d+)?)'
    )
    for m in p.finditer(text):
        a, b = float(m.group(1)), float(m.group(2))
        if abs(a) <= 90 and abs(b) <= 180:
            return normalize_pair(a, b, "decimal_degrees", m.group(0), source)
    return None

def parse_hemi_decimal(text, source):
    p = re.compile(
        r'(?i)([+-]?\d{1,3}(?:\.\d+)?)\s*([NS])\s*[,;/ ]+\s*'
        r'([+-]?\d{1,3}(?:\.\d+)?)\s*([EW])'
    )
    m = p.search(text)
    if not m:
        return None
    lat = float(m.group(1)) * (1 if m.group(2).upper()=="N" else -1)
    lon = float(m.group(3)) * (1 if m.group(4).upper()=="E" else -1)
    return normalize_pair(lat, lon, "hemisphere_decimal", m.group(0), source)

def parse_dms(text, source):
    p = re.compile(
        r'(?i)(\d{1,3})\s*[°º]\s*(\d{1,2})?\s*[\'′]?\s*'
        r'(\d{1,2}(?:\.\d+)?)?\s*[\"″]?\s*([NS])'
        r'\s*[,;/ ]+\s*'
        r'(\d{1,3})\s*[°º]\s*(\d{1,2})?\s*[\'′]?\s*'
        r'(\d{1,2}(?:\.\d+)?)?\s*[\"″]?\s*([EW])'
    )
    m = p.search(text)
    if not m:
        return None
    lat = dms_to_decimal(m.group(1), m.group(2) or 0, m.group(3) or 0, m.group(4))
    lon = dms_to_decimal(m.group(5), m.group(6) or 0, m.group(7) or 0, m.group(8))
    return normalize_pair(lat, lon, "degrees_minutes_seconds", m.group(0), source, .98)

def parse_dm(text, source):
    p = re.compile(
        r'(?i)(\d{1,3})\s*[°º]\s*(\d{1,2}(?:\.\d+)?)\s*[\'′]\s*([NS])'
        r'\s*[,;/ ]+\s*(\d{1,3})\s*[°º]\s*(\d{1,2}(?:\.\d+)?)\s*[\'′]\s*([EW])'
    )
    m = p.search(text)
    if not m:
        return None
    lat = dms_to_decimal(m.group(1), m.group(2), 0, m.group(3))
    lon = dms_to_decimal(m.group(4), m.group(5), 0, m.group(6))
    return normalize_pair(lat, lon, "degrees_decimal_minutes", m.group(0), source, .97)

def parse_text(text, source=None) -> List[CoordinateCandidate]:
    source = source or {}
    # More structured formats first.
    for fn in (parse_dms, parse_dm, parse_hemi_decimal, parse_decimal):
        result = fn(text, source)
        if result:
            return [result]
    return []

def derive_coordinates(lat, lon):
    dlat = decimal_to_dms(lat, "N", "S")
    dlon = decimal_to_dms(lon, "E", "W")
    return {
        "wgs84": {"latitude": lat, "longitude": lon, "datum": "WGS84"},
        "decimal_degrees": f"{lat:.8f}, {lon:.8f}",
        "dms": (
            f"{dlat[0]}° {dlat[1]}' {dlat[2]:.3f}\" {dlat[3]}, "
            f"{dlon[0]}° {dlon[1]}' {dlon[2]:.3f}\" {dlon[3]}"
        ),
        "mgrs": MGRS.toMGRS(lat, lon),
        "plus_code": olc.encode(lat, lon),
        "geohash": geohash_encode(lat, lon, 12),
    }

_BASE32 = "0123456789bcdefghjkmnpqrstuvwxyz"

def geohash_encode(lat, lon, precision=12):
    lat_interval = [-90.0, 90.0]
    lon_interval = [-180.0, 180.0]
    bits = []
    even = True
    out = []
    while len(out) < precision:
        interval = lon_interval if even else lat_interval
        value = lon if even else lat
        mid = (interval[0] + interval[1]) / 2
        if value >= mid:
            bits.append(1); interval[0] = mid
        else:
            bits.append(0); interval[1] = mid
        even = not even
        if len(bits) == 5:
            n = 0
            for b in bits: n = n*2+b
            out.append(_BASE32[n])
            bits = []
    return "".join(out)

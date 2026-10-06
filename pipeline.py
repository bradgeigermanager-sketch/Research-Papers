"""Unified OCR + EXIF coordinate extraction."""
from .ocr import ocr
from .parser import parse_text, derive_coordinates
from .exif import extract_exif
from .w3w import words_from_coordinates

def process_image(path, what3words_api_key=""):
    ocr_result = ocr(path)
    ocr_candidates = parse_text(
        ocr_result["text"],
        {"filename": str(path), "source": "ocr"}
    )

    exif_result = extract_exif(path)
    records = []

    for c in ocr_candidates:
        derived = derive_coordinates(c.latitude, c.longitude)
        if what3words_api_key:
            derived["what3words"] = words_from_coordinates(
                c.latitude, c.longitude, what3words_api_key
            )
        records.append({
            "observation_type": "coordinate_from_ocr",
            "raw_text": c.raw_text,
            "latitude": c.latitude,
            "longitude": c.longitude,
            "format": c.format,
            "confidence": c.confidence,
            "source": c.source,
            "derived": derived
        })

    exif_coord = exif_result.get("coordinate_observation")
    if exif_coord:
        derived = derive_coordinates(
            exif_coord["latitude"], exif_coord["longitude"]
        )
        if what3words_api_key:
            derived["what3words"] = words_from_coordinates(
                exif_coord["latitude"], exif_coord["longitude"],
                what3words_api_key
            )
        records.append({
            "observation_type": "coordinate_from_exif",
            "raw_text": None,
            "latitude": exif_coord["latitude"],
            "longitude": exif_coord["longitude"],
            "format": "EXIF_GPS",
            "confidence": 1.0,
            "source": {
                "filename": str(path),
                "source": "image_exif_gps",
                "fields": exif_coord["source_fields"]
            },
            "derived": derived
        })

    return {
        "parser_version": "1.1.0",
        "image": {
            "filename": str(path)
        },
        "exif": exif_result,
        "ocr": ocr_result,
        "coordinates": records,
        "coordinate_sources": {
            "ocr": [r for r in records if r["observation_type"] == "coordinate_from_ocr"],
            "exif": [r for r in records if r["observation_type"] == "coordinate_from_exif"]
        }
    }

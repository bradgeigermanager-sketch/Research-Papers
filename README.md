# OCR + EXIF Coordinate Parser

The system now processes **both visible coordinates in an image and coordinate
metadata embedded in the image's EXIF data**.

## Unified provenance model

Each coordinate is represented as an observation:

```text
Image
├── OCR observation
│   ├── original OCR text
│   ├── OCR bounding boxes
│   ├── recognized coordinate syntax
│   └── normalized WGS84 coordinate
│
└── EXIF observation
    ├── GPSLatitude
    ├── GPSLatitudeRef
    ├── GPSLongitude
    ├── GPSLongitudeRef
    └── normalized WGS84 coordinate
```

Both observations are converted into the same derived coordinate layer:

```text
WGS84
├── Decimal Degrees
├── DMS
├── MGRS
├── Plus Code / Open Location Code
├── Geohash
├── optional What3Words
└── KML
```

## Why keep OCR and EXIF separate?

They are independent observations. For example, a photograph may show a
printed GPS coordinate that differs from the camera's embedded GPS position.
The system therefore does **not silently choose one**.

A later reconciliation stage can compare:

```text
OCR coordinate
        │
        ├── distance comparison ──┐
        │                         │
EXIF coordinate                   ↓
                              Agreement /
                              discrepancy
```

This makes the output suitable for provenance analysis.

## EXIF fields

The parser preserves general EXIF metadata and GPS metadata where available,
including camera/device information, timestamp fields, and GPS-specific fields.
The coordinate conversion specifically uses:

- GPSLatitude
- GPSLatitudeRef
- GPSLongitude
- GPSLongitudeRef

EXIF GPS coordinates are interpreted as WGS84 geographic coordinates for the
normalized coordinate layer.

## CLI

```bash
python app/cli.py image.jpg --output result.json --kml coordinates.kml
```

Optional What3Words:

```bash
python app/cli.py image.jpg --w3w-api-key YOUR_KEY
```

## API

```bash
uvicorn app.main:app --reload
```

POST an image to `/parse`.

## Recommended next extension

Add a reconciliation engine that calculates the geodesic distance between
every OCR-derived coordinate and every EXIF-derived coordinate, classifies
agreement/disagreement, and records the result as another provenance edge.

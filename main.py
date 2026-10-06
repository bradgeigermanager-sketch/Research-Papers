import os
import tempfile
from pathlib import Path
from fastapi import FastAPI, UploadFile, File, Form
from .pipeline import process_image
from .kml import make_kml

app = FastAPI(title="OCR + EXIF Coordinate Parser", version="1.1.0")

@app.post("/parse")
async def parse_coordinate_image(
    file: UploadFile = File(...),
    what3words_api_key: str = Form(default="")
):
    suffix = Path(file.filename or ".jpg").suffix or ".jpg"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        path = tmp.name

    try:
        result = process_image(path, what3words_api_key)
        # Generate KML in the temporary processing directory.
        kml_path = Path(path).with_suffix(".kml")
        make_kml(result["coordinates"], kml_path)
        result["kml_path"] = str(kml_path)
        return result
    finally:
        # The API result intentionally exposes processing metadata, not a
        # downloadable file URL. A production deployment should stream/store
        # the KML artifact.
        pass

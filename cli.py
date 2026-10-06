import argparse, json
from pathlib import Path
from .pipeline import process_image
from .kml import make_kml

def main():
    ap = argparse.ArgumentParser(description="OCR + EXIF coordinate parser")
    ap.add_argument("image")
    ap.add_argument("--output", default="result.json")
    ap.add_argument("--kml", default="coordinates.kml")
    ap.add_argument("--w3w-api-key", default="")
    args = ap.parse_args()

    result = process_image(args.image, args.w3w_api_key)
    Path(args.output).write_text(json.dumps(result, indent=2, default=str), encoding="utf-8")
    make_kml(result["coordinates"], args.kml)
    print(json.dumps(result, indent=2, default=str))

if __name__ == "__main__":
    main()

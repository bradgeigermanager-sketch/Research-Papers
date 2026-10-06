import cv2
import pytesseract
from PIL import Image
import numpy as np

def preprocess(image_path):
    img = cv2.imread(str(image_path))
    if img is None:
        raise ValueError(f"Cannot read image: {image_path}")
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    scale = 2
    gray = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_CUBIC)
    gray = cv2.GaussianBlur(gray, (3,3), 0)
    return cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

def ocr(image_path):
    img = preprocess(image_path)
    data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT, config="--psm 6")
    words = []
    for i, text in enumerate(data["text"]):
        text = text.strip()
        if not text:
            continue
        words.append({
            "text": text,
            "left": int(data["left"][i]),
            "top": int(data["top"][i]),
            "width": int(data["width"][i]),
            "height": int(data["height"][i]),
            "confidence": float(data["conf"][i]) if str(data["conf"][i]).strip() else -1
        })
    full_text = " ".join(w["text"] for w in words)
    return {"text": full_text, "words": words}

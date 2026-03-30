"""
video_filters.py — Real-Time Video Processing Filters
Provides 7 algorithms that transform a BGR frame into a styled output BGR frame.
Each function accepts and returns a NumPy BGR image array.
"""
import cv2
import numpy as np


FILTER_DISPLAY_NAMES = {
    "original":  "Original",
    "grayscale": "Black & White",
    "heatmap":   "Heat Signature",
    "canny":     "Canny Edge",
    "sketch":    "Pencil Sketch",
    "cartoon":   "Cartoon",
    "emboss":    "Emboss Relief",
    "negative":  "Negative / Invert",
}

FILTER_IDS = list(FILTER_DISPLAY_NAMES.keys())


# ─────────────────────────────────────────────
# 1. Original (no-op)
# ─────────────────────────────────────────────
def filter_original(frame: np.ndarray) -> np.ndarray:
    return frame.copy()


# ─────────────────────────────────────────────
# 2. Black & White (Grayscale)
# ─────────────────────────────────────────────
def filter_grayscale(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    return cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)


# ─────────────────────────────────────────────
# 3. Heat Signature (Infrared / Thermal look)
# ─────────────────────────────────────────────
def filter_heatmap(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    heat = cv2.applyColorMap(gray, cv2.COLORMAP_JET)
    return heat


# ─────────────────────────────────────────────
# 4. Canny Edge Detection
# ─────────────────────────────────────────────
def filter_canny(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, threshold1=50, threshold2=150)
    # Invert for white-on-black look; convert back to BGR
    edges_inv = cv2.bitwise_not(edges)
    return cv2.cvtColor(edges_inv, cv2.COLOR_GRAY2BGR)


# ─────────────────────────────────────────────
# 5. Pencil Sketch
# ─────────────────────────────────────────────
def filter_sketch(frame: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    # Smooth to reduce noise
    blurred = cv2.medianBlur(gray, 5)
    # Invert and blur
    inv = cv2.bitwise_not(blurred)
    inv_blur = cv2.GaussianBlur(inv, (21, 21), 0)
    # Dodge blend
    sketch = cv2.divide(blurred, cv2.bitwise_not(inv_blur), scale=256.0)
    return cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)


# ─────────────────────────────────────────────
# 6. Cartoon Effect
# ─────────────────────────────────────────────
def filter_cartoon(frame: np.ndarray) -> np.ndarray:
    # Step 1: Smooth color regions
    color = cv2.bilateralFilter(frame, d=9, sigmaColor=300, sigmaSpace=300)
    # Step 2: Edge mask from grayscale
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_blur = cv2.medianBlur(gray, 7)
    edges = cv2.adaptiveThreshold(
        gray_blur, 255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY, blockSize=9, C=2
    )
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    # Step 3: Combine: mask edges onto smooth color
    cartoon = cv2.bitwise_and(color, edges_bgr)
    return cartoon


# ─────────────────────────────────────────────
# 7. Emboss Relief
# ─────────────────────────────────────────────
def filter_emboss(frame: np.ndarray) -> np.ndarray:
    kernel = np.array([
        [-2, -1,  0],
        [-1,  1,  1],
        [ 0,  1,  2]
    ], dtype=np.float32)
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    embossed = cv2.filter2D(gray, ddepth=-1, kernel=kernel)
    # Shift gray level to center midtones
    embossed = np.clip(embossed + 128, 0, 255).astype(np.uint8)
    return cv2.cvtColor(embossed, cv2.COLOR_GRAY2BGR)


# ─────────────────────────────────────────────
# 8. Negative / Invert
# ─────────────────────────────────────────────
def filter_negative(frame: np.ndarray) -> np.ndarray:
    return cv2.bitwise_not(frame)


# ─────────────────────────────────────────────
# Dispatcher
# ─────────────────────────────────────────────
_FILTER_MAP = {
    "original":  filter_original,
    "grayscale": filter_grayscale,
    "heatmap":   filter_heatmap,
    "canny":     filter_canny,
    "sketch":    filter_sketch,
    "cartoon":   filter_cartoon,
    "emboss":    filter_emboss,
    "negative":  filter_negative,
}

def apply_filter(frame: np.ndarray, filter_id: str) -> np.ndarray:
    """Apply the named filter to a BGR frame. Falls back to original if unknown."""
    fn = _FILTER_MAP.get(filter_id, filter_original)
    try:
        return fn(frame)
    except Exception:
        return frame.copy()

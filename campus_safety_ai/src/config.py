import os

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Model configurations
MODELS_DIR = os.path.join(BASE_DIR, 'models')
# YOLOv11 — ultralytics auto-downloads on first run
# Options: yolo11n.pt / yolo11s.pt / yolo11m.pt / yolo11l.pt / yolo11x.pt
YOLO_MODEL_PATH = 'yolo11n.pt'

# Device configuration (Auto-detecting GPU)
import torch
DEVICE = 'cuda' if torch.cuda.is_available() else 'cpu'

# Dataset paths
FACES_DATASET_DIR = os.path.join(BASE_DIR, 'data', 'faces_dataset')

# Log settings
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
ALERTS_LOG_PATH = os.path.join(LOGS_DIR, 'alerts_log.csv')

# Alert screenshot folder
SCREENSHOTS_DIR = os.path.join(BASE_DIR, 'web', 'static', 'images', 'alerts')

# Video Stream Source (Can be overridden by CLI args)
DEFAULT_VIDEO_SOURCE = 0
VIDEO_SOURCE = os.getenv('VIDEO_SOURCE', DEFAULT_VIDEO_SOURCE)

# Convert string source to int if it's a digit (for webcam IDs)
try:
    if str(VIDEO_SOURCE).isdigit():
        VIDEO_SOURCE = int(VIDEO_SOURCE)
except:
    pass

# Detection thresholds
CONFIDENCE_THRESHOLD = 0.45  # Slightly lower for more sensitive detection on GPU
IOU_THRESHOLD = 0.45

# Crowd analysis config
CROWD_LIMIT = 10  # Max people allowed in frame before density alert

# Alert types
ALERT_HIGH_PRIORITY = "HIGH-PRIORITY"
ALERT_MEDIUM_PRIORITY = "MEDIUM-PRIORITY"
ALERT_LOW_PRIORITY = "LOW-PRIORITY"

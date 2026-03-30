from ultralytics import YOLO
import torch
from campus_safety_ai.src import config

class ObjectDetector:
    """YOLOv11 Object Detector for people, vehicles, etc. — higher precision than v8."""
    def __init__(self, model_path=config.YOLO_MODEL_PATH):
        self.model = YOLO(model_path)
        self.device = config.DEVICE
        self.model.to(self.device)
        
    def detect(self, frame):
        """Perform object detection on single frame."""
        results = self.model.predict(
            source=frame,
            conf=config.CONFIDENCE_THRESHOLD,
            iou=config.IOU_THRESHOLD,
            device=self.device,
            verbose=False
        )
        
        detections = []
        for result in results:
            for box in result.boxes:
                cls = int(box.cls[0])
                conf = float(box.conf[0])
                label = self.model.names[cls]
                coords = box.xyxy[0].tolist()  # [x1, y1, x2, y2]
                
                detections.append({
                    'label': label,
                    'confidence': conf,
                    'bbox': [int(c) for c in coords],
                    'class_id': cls
                })
        
        return detections

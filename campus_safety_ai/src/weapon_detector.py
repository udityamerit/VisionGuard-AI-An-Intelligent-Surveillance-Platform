from campus_safety_ai.src.object_detection import ObjectDetector
from campus_safety_ai.src import config

class WeaponDetector(ObjectDetector):
    """Specific detector for weapons using COCO classes or custom if trained."""
    def __init__(self, model_path=config.YOLO_MODEL_PATH):
        super().__init__(model_path)
        
        # Mapping COCO class IDs for common weapons if standard YOLOv8 weights are used
        # (knife: 43, gun: 73 or similar in some datasets)
        # Note: COCO does not have 'gun', it usually has 'knife'.
        # We will check if the model has 'knife' or 'gun' classes.
        self.weapon_classes = ['knife', 'gun', 'weapon', 'pistol', 'rifle']
        
    def detect_weapons(self, frame):
        """Filter detections to only weapons."""
        detections = self.detect(frame)
        weapons = [d for d in detections if d['label'].lower() in self.weapon_classes]
        return weapons

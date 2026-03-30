import cv2
import numpy as np

class FightDetector:
    """Action Recognition Module: Detects violent movements/boxing via bbox analysis and optical flow."""
    def __init__(self):
        self.prev_gray = None
        self.flow_thresh = 4.0  # Magnitude of movement to trigger violence alert
        
    def detect(self, person_bboxes, current_frame):
        """Analyzes people intersections and optical flow magnitude."""
        if len(person_bboxes) < 2:
            return False  # Need at least 2 people for a fight
        
        gray = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        
        # Check for Overlapping Bounding Boxes
        for i, bbox1 in enumerate(person_bboxes):
            for j, bbox2 in enumerate(person_bboxes):
                if i != j:
                    if self.check_intersection(bbox1, bbox2):
                        # BBoxes overlap - possible contact
                        # Now analyze movement magnitude in that area
                        if self.prev_gray is not None:
                            flow = cv2.calcOpticalFlowFarneback(self.prev_gray, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
                            mag, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
                            
                            # Get ROI magnitude
                            roi_mag = mag[bbox1[1]:bbox1[3], bbox1[0]:bbox1[2]]
                            if roi_mag.size > 0 and np.mean(roi_mag) > self.flow_thresh:
                                self.prev_gray = gray
                                return True
        
        self.prev_gray = gray
        return False
        
    def check_intersection(self, boxA, boxB):
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)
        return interArea > 0

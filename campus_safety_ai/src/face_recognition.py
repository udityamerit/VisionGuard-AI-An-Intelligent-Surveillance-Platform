from deepface import DeepFace
import os
import cv2
import pandas as pd
from campus_safety_ai.src import config

class FaceRecognizer:
    """Face recognition module using DeepFace and FAISS/CSV-based lookups."""
    def __init__(self, db_path=config.FACES_DATASET_DIR):
        self.db_path = db_path
        if not os.path.exists(self.db_path):
            os.makedirs(self.db_path)
            
    def identify(self, frame):
        """Identify faces in frame."""
        try:
            # We search for faces in the db_path
            # Note: DeepFace.find downloads weights if not present
            results = DeepFace.find(
                img_path=frame,
                db_path=self.db_path,
                model_name="VGG-Face",
                enforce_detection=False,
                silent=True
            )
            
            identities = []
            if len(results) > 0 and not results[0].empty:
                for res in results:
                    identity = res['identity'].values[0]
                    name = os.path.basename(os.path.dirname(identity)) if '/' in identity or '\\' in identity else "Authorized"
                    identities.append(name)
            else:
                identities.append("Unknown")
            
            return identities
        except Exception as e:
            # Return Unknown if error or no face detected
            return ["Unknown"]

    def add_face(self, frame, name):
        """Save a face to the dataset."""
        person_dir = os.path.join(self.db_path, name)
        if not os.path.exists(person_dir):
            os.makedirs(person_dir)
        
        filename = f"{name}_{len(os.listdir(person_dir))}.jpg"
        path = os.path.join(person_dir, filename)
        cv2.imwrite(path, frame)
        return path

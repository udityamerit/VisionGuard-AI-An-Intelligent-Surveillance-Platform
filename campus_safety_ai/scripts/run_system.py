import sys
import os
import threading
import time
import cv2
import argparse

# Add project root parent to sys.path to allow package imports
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(PROJECT_ROOT))

from campus_safety_ai.src.video_stream import VideoStream
from campus_safety_ai.src.object_detection import ObjectDetector
from campus_safety_ai.src.weapon_detector import WeaponDetector
from campus_safety_ai.src.object_tracking import SortTracker
from campus_safety_ai.src.face_recognition import FaceRecognizer
from campus_safety_ai.src.fight_detector import FightDetector
from campus_safety_ai.src.crowd_analysis import CrowdAnalyzer
from campus_safety_ai.src.anomaly_detector import AnomalyDetector
from campus_safety_ai.src.alert_system import AlertSystem
from campus_safety_ai.src import config, utils
from campus_safety_ai.web import app as flask_app

def get_args():
    parser = argparse.ArgumentParser(description="AI Campus Safety Surveillance System")
    parser.add_argument("--source", type=str, default=None,
                        help="Video source: 0 for webcam, filename.mp4 for video, or RTSP URL for IP camera.")
    parser.add_argument("--skip", type=int, default=2,
                        help="Frame skipping for performance (default: 2)")
    return parser.parse_args()

def select_input_interactive():
    # Deprecated: Selection moved to Web Dashboard
    return "0"

class CampusSafetySystem:
    def __init__(self, source=None, skip=2):
        print(f"--- Initializing AI Campus Safety System (Device: {config.DEVICE}) ---")
        # Handle source type (int for webcam, str for others)
        self.video_source = int(source) if str(source).isdigit() else source
        
        self.stream = None
        if self.video_source is not None:
            self.stream = VideoStream(self.video_source).start()
        
        self.obj_detector = ObjectDetector()
        self.weapon_detector = WeaponDetector()
        self.tracker = SortTracker()
        self.face_recognizer = FaceRecognizer()
        self.fight_detector = FightDetector()
        self.crowd_analyzer = CrowdAnalyzer()
        self.anomaly_detector = AnomalyDetector()
        self.alert_system = AlertSystem()
        
        self.running = True
        self.frame_skip = skip
        self.frame_count = 0

    def change_source(self, source):
        """Update the video source dynamically with path resolution."""
        print(f"--- Attempting to change source to: {source} ---")
        
        # Stop existing stream if running
        if self.stream:
            self.stream.stop()
            time.sleep(0.5) # Give it time to release hardware
        
        # 1. Handle Integer sources (Webcams)
        if str(source).isdigit():
            self.video_source = int(source)
        # 2. Handle File/URL sources
        else:
            # If it's a relative path starting with 'data/', resolve it from BASE_DIR
            if source.startswith('data/') or source.startswith('data\\'):
                full_path = os.path.join(config.BASE_DIR, source)
                if os.path.exists(full_path):
                    self.video_source = full_path
                else:
                    print(f"Warning: File not found at {full_path}. Using raw input.")
                    self.video_source = source
            else:
                self.video_source = source

        print(f"--- New source set to: {self.video_source} ---")
        
        # Initialize and start new stream
        try:
            self.stream = VideoStream(self.video_source).start()
            return True
        except Exception as e:
            print(f"Error starting new stream: {e}")
            return False

    def run_cv_pipeline(self):
        """Threaded job to process CV pipeline."""
        print("--- Starting AI Engine Loop ---")
        while self.running:
            try:
                if self.stream is None or not self.stream.is_opened():
                    time.sleep(1)
                    continue

                frame = self.stream.read()
                
                # Resiliency check: Skip if frame is not yet ready or stream is offline
                if frame is None:
                    time.sleep(0.1)
                    continue

                self.frame_count += 1
                if self.frame_count % self.frame_skip != 0:
                    # Still update the shared frame for live feed (even if no AI on this frame)
                    flask_app.current_frame = frame
                    continue

                # 1. Object Detection
                detections = self.obj_detector.detect(frame)
                
                # 2. Weapon Detection
                _ = self.weapon_detector.detect_weapons(frame) # Keep sensor active
                
                # 3. Face Recognition
                identities = self.face_recognizer.identify(frame)
                
                # 4. Crowd Analysis
                crowd_info = self.crowd_analyzer.analyze(detections)
                
                # 5. Fight Detection
                person_bboxes = [d['bbox'] for d in detections if d['label'].lower() == 'person']
                is_fighting = self.fight_detector.detect(person_bboxes, frame)
                
                # 6. Anomaly Detection Engine
                anomalies = self.anomaly_detector.check_anomalies(
                    detections, 
                    identities, 
                    is_fighting, 
                    crowd_info['is_overcrowded']
                )
                
                # 7. Alert System
                for anomaly in anomalies:
                    # Capture a marked frame for high-precision alerts
                    marked_frame = frame.copy()
                    self.annotate_frame(marked_frame, detections, identities, is_fighting, crowd_info)
                    self.alert_system.trigger_alert(marked_frame, anomaly)
                
                # Update the GLOBAL AI RESULTS for asynchronous rendering in Flask
                flask_app.active_ai_results = {
                    "detections": detections,
                    "identities": identities,
                    "is_fighting": is_fighting,
                    "crowd_info": crowd_info,
                    "timestamp": time.time()
                }
                
                # Moderate sleep to prevent CPU bottlenecking
                time.sleep(0.01)

            except Exception as e:
                print(f"Error in CV pipeline: {e}")
                time.sleep(1)
        
        print("--- CV Loop Stopped ---")

    def annotate_frame(self, frame, detections, identities, is_fighting, crowd_info):
        """Draw system metadata on the frame."""
        for i, det in enumerate(detections):
            bbox = det['bbox']
            label = det['label']
            color = (56, 189, 248) # Default Blue Accent
            
            if label.lower() in ['knife', 'gun']:
                color = (0, 0, 255) # Red for weapons
            
            cv2.rectangle(frame, (bbox[0], bbox[1]), (bbox[2], bbox[3]), color, 2)
            cv2.putText(frame, label, (bbox[0], bbox[1]-10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
        
        # Info Panel
        info_lines = [
            f"People Count: {crowd_info['count']}",
            f"Density: {crowd_info['status']}",
            f"Violence: {'YES' if is_fighting else 'NO'}",
            f"FPS: {28.4}" # Placeholder for real calculation
        ]
        utils.draw_info_panel(frame, info_lines)

    def start(self):
        # Start AI Loop in thread
        ai_thread = threading.Thread(target=self.run_cv_pipeline, daemon=True)
        ai_thread.start()
        
        # Start Flask Dashboard (blocking on the main thread)
        print("--- Starting Monitoring Dashboard (http://127.0.0.1:5000) ---")
        flask_app.app.run(debug=False, port=5000, host='0.0.0.0')

if __name__ == "__main__":
    args = get_args()
    
    # Start in idle mode (None) if no source provided, or use CLI arg
    source = args.source
    
    system = CampusSafetySystem(source=source, skip=args.skip)
    
    # Expose system to Flask app
    flask_app.app.system = system
    
    try:
        system.start()
    except KeyboardInterrupt:
        print("\nExiting system gracefully...")
        system.running = False
        if system.stream:
            system.stream.stop()
        sys.exit(0)

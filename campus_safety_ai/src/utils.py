import cv2
import datetime
import os
import pandas as pd
from campus_safety_ai.src import config

def get_current_timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def get_screenshot_filename(threat_type):
    return f"{threat_type.lower().replace(' ', '_')}_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"

def draw_info_panel(frame, info_list):
    """Draws a semi-transparent panel with system info."""
    overlay = frame.copy()
    cv2.rectangle(overlay, (10, 10), (250, 40 + (len(info_list) * 25)), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)
    
    y = 35
    for info in info_list:
        cv2.putText(frame, info, (20, y), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        y += 25

def log_alert(threat_type, camera_id="CAM_01"):
    """Log threat event to CSV log."""
    timestamp = get_current_timestamp()
    screenshot_name = get_screenshot_filename(threat_type)
    
    data = {
        'timestamp': [timestamp],
        'camera_id': [camera_id],
        'threat_type': [threat_type],
        'screenshot': [screenshot_name]
    }
    
    df = pd.DataFrame(data)
    if not os.path.exists(config.ALERTS_LOG_PATH):
        df.to_csv(config.ALERTS_LOG_PATH, index=False)
    else:
        df.to_csv(config.ALERTS_LOG_PATH, mode='a', header=False, index=False)
        
    return screenshot_name

def save_screenshot(frame, filename):
    """Save alert frame to static folder."""
    if not os.path.exists(config.SCREENSHOTS_DIR):
        os.makedirs(config.SCREENSHOTS_DIR)
    
    path = os.path.join(config.SCREENSHOTS_DIR, filename)
    cv2.imwrite(path, frame)
    return path

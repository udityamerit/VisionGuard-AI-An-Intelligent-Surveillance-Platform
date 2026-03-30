import os
import requests
import sys

# Add project parent directory to sys.path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.dirname(PROJECT_ROOT))

from campus_safety_ai.src import config

def setup_directories():
    print("--- Setting up Project Directories ---")
    dirs = [
        config.FACES_DATASET_DIR,
        os.path.join(PROJECT_ROOT, 'data', 'videos'),
        config.SCREENSHOTS_DIR,
        config.LOGS_DIR,
        config.MODELS_DIR
    ]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"Created: {d}")

def download_sample_data():
    print("\n--- Downloading Specialized Surveillance Data ---")
    
    # Comprehensive test suite for security scenarios
    sample_videos = {
        "general_traffic.mp4": "https://raw.githubusercontent.com/intel-iot-devkit/sample-videos/master/person-bicycle-car-detection.mp4",
        "violence_clash.mp4": "https://github.com/intel-iot-devkit/sample-videos/raw/master/face-demographics-walking.mp4",  # Placeholder for high movement
        "crowd_density.mp4": "https://github.com/intel-iot-devkit/sample-videos/raw/master/store-aisle-detection.mp4"    # High density area
    }

    print("Tip: These clips are for testing different AI sensors (Detection, Crowds, Tracking).")

    video_dir = os.path.join(PROJECT_ROOT, 'data', 'videos')
    if not os.path.exists(video_dir):
        os.makedirs(video_dir)

    for name, url in sample_videos.items():
        target_path = os.path.join(video_dir, name)
        if not os.path.exists(target_path):
            print(f"Fetching {name}...", end=" ", flush=True)
            try:
                response = requests.get(url, stream=True, timeout=30)
                if response.status_code == 200:
                    with open(target_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=8192):
                            f.write(chunk)
                    print("[DONE]")
                else:
                    print(f"[FAILED: {response.status_code}]")
            except Exception as e:
                print(f"[ERROR: {e}]")
        else:
            print(f"Source {name} already available locally.")

def setup_face_dataset():
    print("\n--- Preparing Identity Verification Database ---")
    instruction_path = os.path.join(config.FACES_DATASET_DIR, "README_FACE_SETUP.txt")
    
    content = """HOW TO SETUP FACE RECOGNITION:
1. Create a folder with the Person's Name inside 'data/faces_dataset/'
2. Example: Create 'data/faces_dataset/John_Smith/'
3. Place 1-2 clear JPG photos of John inside that folder.
4. The system will now recognize him as 'John_Smith' instead of 'Unknown'."""

    with open(instruction_path, "w") as f:
        f.write(content)
    
    print(f"Created face setup guide at: {instruction_path}")
    
    # Create one sample demo folder
    demo_dir = os.path.join(config.FACES_DATASET_DIR, 'Authorized_Staff_Demo')
    if not os.path.exists(demo_dir):
        os.makedirs(demo_dir)
        print(f"Created demo identity folder: {demo_dir}")

if __name__ == "__main__":
    setup_directories()
    download_sample_data()
    setup_face_dataset()
    print("\n--- Dataset Setup Complete! ---")
    print("Project is ready for multi-input testing.")

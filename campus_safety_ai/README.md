# AI Campus Safety Surveillance System

A production-grade intelligent surveillance platform for schools, universities, and commercial campuses. Using state-of-the-art Deep Learning (YOLOv8, DeepFace, SORT) to detect security threats in real-time.

## 🚀 Vision
Automating campus security by identifying weapons, violence, unauthorized individuals, and overcrowding without constant human monitoring.

## 🏗️ System Architecture
The system follows a multi-stage modular pipeline:
1.  **Video Ingestion**: Multi-threaded capture from CCTV/Webcams.
2.  **Object Detection**: YOLOv8 extracts people, vehicles, and weapons.
3.  **Identification**: DeepFace compares detected faces against the `faces_dataset/`.
4.  **Action Recognition**: Heuristic-based fight detection utilizing optical flow and bbox intersection.
5.  **Anomaly Engine**: Rules-based logic to determine "threat levels."
6.  **Alert & UI**: Automated logging and a modern Flask Dashboard for security personnel.

## 🛠️ Tech Stack
-   **Backend**: Python 3.10+, OpenCV, PyTorch.
-   **AI Models**: YOLOv8 (Detection), DeepFace (Recognition), SORT (Tracking).
-   **Web Interface**: Flask, Bootstrap 5, Chart.js, Glassmorphism UI.
-   **Database**: FAISS / CSV for alert logs.

## 📂 Project Structure
```text
campus_safety_ai/
├── data/
│   ├── videos/
│   └── faces_dataset/
├── models/
├── src/
│   ├── config.py
│   ├── video_stream.py
│   ├── object_detection.py
│   ├── ... (all CV modules)
├── web/
│   ├── app.py
│   ├── templates/
│   └── static/
├── scripts/
│   └── run_system.py
└── requirements.txt
```

## ⚙️ Installation
1.  **Clone the Repository**
2.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```
3.  **Setup Known Faces**
    Add folders into `data/faces_dataset/` with names of authorized personnel (e.g. `data/faces_dataset/John/image1.jpg`).

## 🚦 How to Run
1.  **Connect Camera**: Ensure your webcam or IP camera is accessible.
2.  **Configure `src/config.py`**: Update `VIDEO_SOURCE` if using an IP URL.
3.  **Execute**:
    ```bash
    python scripts/run_system.py
    ```
4.  **Monitor**: Open your browser at `http://127.0.0.1:5000`.

## 🛡️ Core Features
-   **Real-time Threat Detection**: Immediate identification of knives/guns.
-   **Violence Detection**: Alerts on fighting or aggressive behavior.
-   **Identity Verification**: Distinguishes between authorized staff and unknown visitors.
-   **Live Monitoring Dashboard**: Professional dark-mode UI with telemetry metadata.
-   **Automatic Alert Logging**: Every incident is screenshotted and timestamped.

---
*Developed for AI Campus Safety & Surveillance Researchers.*

from flask import Flask, render_template, Response, jsonify, request, current_app, send_file
import cv2
import os
import tempfile
import pandas as pd
from werkzeug.utils import secure_filename
from campus_safety_ai.src import config
from campus_safety_ai.src.video_filters import apply_filter, FILTER_DISPLAY_NAMES, FILTER_IDS

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(config.BASE_DIR, 'data', 'videos')

@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Handle video file uploads."""
    if 'video' not in request.files:
        return jsonify({"status": "error", "message": "No file part"}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({"status": "error", "message": "No selected file"}), 400
    
    if file:
        filename = secure_filename(file.filename)
        if not os.path.exists(app.config['UPLOAD_FOLDER']):
            os.makedirs(app.config['UPLOAD_FOLDER'])
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({
            "status": "success",
            "message": "File uploaded successfully",
            "filename": filename,
            "path": f"data/videos/{filename}"
        })

# ── Global State ──────────────────────────────────────────────────────────────
active_ai_results = {
    "detections": [],
    "identities": [],
    "is_fighting": False,
    "crowd_info": {"count": 0, "status": "Low", "is_overcrowded": False}
}
active_filter = "original"

import time


def generate_frames():
    """MJPEG stream that renders the latest AI data onto the raw frame."""
    global active_ai_results
    while True:
        frame = None
        if hasattr(app, 'system') and app.system.stream:
            frame = app.system.stream.read()

        if frame is not None:
            try:
                if hasattr(app, 'system'):
                    app.system.annotate_frame(
                        frame,
                        active_ai_results['detections'],
                        active_ai_results['identities'],
                        active_ai_results['is_fighting'],
                        active_ai_results['crowd_info']
                    )
                ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if not ret:
                    time.sleep(0.01)
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            except Exception:
                time.sleep(0.01)
                continue
        else:
            time.sleep(0.1)


def generate_processed_frames():
    """MJPEG stream with the active filter applied — no AI annotations."""
    global active_filter
    while True:
        frame = None
        if hasattr(app, 'system') and app.system.stream:
            frame = app.system.stream.read()

        if frame is not None:
            try:
                processed = apply_filter(frame, active_filter)
                ret, buffer = cv2.imencode('.jpg', processed, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if not ret:
                    time.sleep(0.01)
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            except Exception:
                time.sleep(0.01)
                continue
        else:
            time.sleep(0.1)


def generate_clean_frames():
    """MJPEG stream of raw frames with NO AI annotations (for Filter Lab original feed)."""
    while True:
        frame = None
        if hasattr(app, 'system') and app.system.stream:
            frame = app.system.stream.read()

        if frame is not None:
            try:
                ret, buffer = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
                if not ret:
                    time.sleep(0.01)
                    continue
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')
            except Exception:
                time.sleep(0.01)
                continue
        else:
            time.sleep(0.1)


# ── Page Routes ───────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


@app.route('/filterlab')
def filterlab():
    return render_template('filterlab.html',
                           filters=FILTER_DISPLAY_NAMES,
                           active_filter=active_filter)


@app.route('/alerts')
def alerts():
    alerts_data = []
    if os.path.exists(config.ALERTS_LOG_PATH):
        df = pd.read_csv(config.ALERTS_LOG_PATH)
        alerts_data = df.iloc[::-1].to_dict('records')
    return render_template('alerts.html', alerts=alerts_data)


@app.route('/analytics')
def analytics():
    return render_template('analytics.html')


# ── Video Feed Routes ─────────────────────────────────────────────────────────
@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_clean')
def video_feed_clean():
    """Clean raw feed with no AI annotations — used by Filter Lab."""
    return Response(generate_clean_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/video_feed_processed')
def video_feed_processed():
    return Response(generate_processed_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# ── Filter API ────────────────────────────────────────────────────────────────
@app.route('/api/set_filter', methods=['POST'])
def set_filter():
    """Set the active video processing filter."""
    global active_filter
    data = request.json or {}
    requested = data.get('filter', 'original')
    if requested in FILTER_IDS:
        active_filter = requested
        return jsonify({"status": "success", "filter": active_filter})
    return jsonify({"status": "error", "message": f"Unknown filter: {requested}"}), 400


@app.route('/api/download_processed')
def download_processed():
    """
    Re-process the full video source with the active filter and
    serve the complete output .mp4 for download.
    """
    global active_filter

    source = None
    if hasattr(app, 'system'):
        source = app.system.video_source

    if source is None:
        return jsonify({"status": "error", "message": "No video source active."}), 400

    cap = cv2.VideoCapture(source)
    if not cap.isOpened():
        return jsonify({"status": "error",
                        "message": "Cannot open video source for export."}), 500

    fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    tmp_dir = tempfile.mkdtemp()
    out_path = os.path.join(tmp_dir, f"processed_{active_filter}.mp4")
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    writer = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            processed = apply_filter(frame, active_filter)
            writer.write(processed)
    finally:
        cap.release()
        writer.release()

    filter_name = FILTER_DISPLAY_NAMES.get(active_filter, active_filter).replace(" ", "_")
    download_name = f"visionguard_{filter_name}.mp4"
    return send_file(out_path, mimetype='video/mp4',
                     as_attachment=True, download_name=download_name)


# ── Source Control API ────────────────────────────────────────────────────────
@app.route('/api/sources')
def list_sources():
    """List available video files in the data directory."""
    video_dir = os.path.join(config.BASE_DIR, 'data', 'videos')
    videos = []
    if os.path.exists(video_dir):
        videos = [f for f in os.listdir(video_dir)
                  if f.endswith(('.mp4', '.avi', '.mov'))]
    return jsonify({
        "files": videos,
        "active_source": current_app.system.video_source if hasattr(current_app, 'system') else None
    })


@app.route('/api/start_stream', methods=['POST'])
def start_stream():
    """Trigger the system to change source."""
    data = request.json
    source = data.get('source', '0')
    if hasattr(current_app, 'system'):
        success = current_app.system.change_source(source)
        if success:
            return jsonify({"status": "success", "message": f"Source changed to {source}"})
        else:
            return jsonify({"status": "error",
                            "message": f"Failed to initialize source: {source}"})
    return jsonify({"status": "error", "message": "System not initialized"}), 500


# ── Stats API ─────────────────────────────────────────────────────────────────
@app.route('/api/stats')
def get_stats():
    """Return system health and live detection statistics."""
    import psutil
    global active_ai_results
    stats = {
        "cpu": psutil.cpu_percent(),
        "memory": psutil.virtual_memory().percent,
        "status": "Healthy",
        "people_count": active_ai_results['crowd_info']['count'],
        "crowd_status": active_ai_results['crowd_info']['status'],
        "is_fighting": "YES" if active_ai_results['is_fighting'] else "NO",
        "last_update": active_ai_results.get('timestamp', 0)
    }
    return jsonify(stats)


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)

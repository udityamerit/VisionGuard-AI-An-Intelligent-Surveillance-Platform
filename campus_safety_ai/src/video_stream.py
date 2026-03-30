import cv2
import threading
import time

class VideoStream:
    """Threaded Video Stream to prevent blocking the main process."""
    def __init__(self, source=None):
        self.src = source
        self.stream = None
        self.grabbed = False
        self.frame = None
        self.stopped = True
        self.lock = threading.Lock()
        
        if self.src is not None:
            self.stream = cv2.VideoCapture(source)
            (self.grabbed, self.frame) = self.stream.read()
            self.stopped = False

    def start(self):
        threading.Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        """Threaded frame capture loop with basic reconnection."""
        retry_count = 0
        max_retries = 5
        
        while not self.stopped:
            (grabbed, frame) = self.stream.read()
            if not grabbed:
                if retry_count < max_retries:
                    print(f"--- Stream Interrupted. Reconnecting... (Attempt {retry_count+1}) ---")
                    self.stream.release()
                    time.sleep(2)
                    self.stream = cv2.VideoCapture(self.src)
                    retry_count += 1
                    continue
                else:
                    print("--- Stream Error: Failed to reconnect. Stopping thread. ---")
                    self.stopped = True
                    break
            
            # Successful grab
            retry_count = 0
            with self.lock:
                self.grabbed = grabbed
                self.frame = frame
            time.sleep(0.01)  # Throttle to avoid CPU hogging

    def read(self):
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()

    def stop(self):
        self.stopped = True
        self.stream.release()

    def is_opened(self):
        return self.stream.isOpened()

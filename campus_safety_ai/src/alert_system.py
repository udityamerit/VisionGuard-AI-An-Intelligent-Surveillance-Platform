from campus_safety_ai.src import utils, config

class AlertSystem:
    """Handles alert generation, capturing snapshots and logging."""
    def __init__(self):
        self.active_alerts = {}
        self.alert_cooldown = 5  # seconds
        import time
        self.last_alert_time = {}

    def trigger_alert(self, frame, threat_type):
        """Generate a new alert if not in cooldown."""
        import time
        now = time.time()
        
        # Prevent spamming the same alert type too quickly
        if threat_type in self.last_alert_time:
            if now - self.last_alert_time[threat_type] < self.alert_cooldown:
                return None
        
        self.last_alert_time[threat_type] = now
        
        # Log to CSV
        screenshot_filename = utils.log_alert(threat_type)
        
        # Save frame image
        utils.save_screenshot(frame, screenshot_filename)
        
        print(f"!!! ALERT TRIGGERED: {threat_type} !!!")
        return screenshot_filename

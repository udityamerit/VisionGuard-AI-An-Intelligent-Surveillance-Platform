class AnomalyDetector:
    """Combines signals to detect abnormal/suspicious behavior."""
    def __init__(self):
        pass
        
    def check_anomalies(self, detections, identities, is_fighting, is_overcrowded):
        """Analyze various inputs to find suspicious patterns."""
        anomalies = []
        
        # 1. Fighting detected
        if is_fighting:
            anomalies.append("VIOLENCE_DETECTED")
            
        # 2. Unknown person in frame with weapon (hypothetical)
        weapon_detected = any(d['label'].lower() in ['knife', 'gun'] for d in detections)
        if weapon_detected:
            anomalies.append("WEAPON_DETECTED")
            
        # 3. Crowd congestion
        if is_overcrowded:
            anomalies.append("CROWD_CONGESTION")
            
        # 4. Unknown individuals in secure zone
        for identity in identities:
            if identity == "Unknown":
                # Only flag as anomaly if multiple or combined with other signals
                if weapon_detected or is_fighting:
                    anomalies.append("SUSPICIOUS_UNKNOWN_PERSON")
        
        return list(set(anomalies))

from campus_safety_ai.src import config

class CrowdAnalyzer:
    """Estimates density of people in monitored zone."""
    def __init__(self, limit=config.CROWD_LIMIT):
        self.limit = limit
        
    def analyze(self, detections):
        """Analyze if overcrowding is occurring."""
        person_count = sum(1 for d in detections if d['label'].lower() == 'person')
        
        density_status = "NORMAL"
        is_overcrowded = False
        
        if person_count >= self.limit:
            density_status = "OVERCROWDED"
            is_overcrowded = True
        elif person_count > (self.limit * 0.7):
            density_status = "HIGH DENSITY"
            
        return {
            'count': person_count,
            'status': density_status,
            'is_overcrowded': is_overcrowded
        }

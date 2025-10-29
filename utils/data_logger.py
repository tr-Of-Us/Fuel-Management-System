import json
from datetime import datetime
import os

class DataLogger:
    
    def __init__(self, log_file_path="data/logs/system_log.json"):
        """
        Initialize the data logger.
        
        Args:
            log_file_path (str): Path to the log file
        """
        self._log_file_path = log_file_path
        self._log_entries = []
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        log_dir = os.path.dirname(self._log_file_path)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
    
    def log_event(self, event_type, message, tank_id=None, severity="INFO"):
        """
        Log a system event.
        
        Args:
            event_type (str): Type of event (e.g., "FUEL_TRANSFER", "ALERT", "STATUS_CHANGE")
            message (str): Event description
            tank_id (str): Optional tank identifier
            severity (str): Event severity ("INFO", "WARNING", "CRITICAL")
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "message": message,
            "tank_id": tank_id,
            "severity": severity
        }
        self._log_entries.append(entry)
        print(f"[{severity}] {event_type}: {message}")
    
    def log_fuel_level(self, tank_id, fuel_level, capacity, percentage):
        message = f"Fuel level: {fuel_level:.1f}L / {capacity:.1f}L ({percentage:.1f}%)"
        self.log_event("FUEL_LEVEL", message, tank_id, "INFO")
    
    def log_transfer(self, source_tank, destination_tank, amount, success):
        """
        Log fuel transfer operation.
        
        Args:
            source_tank (str): Source tank ID
            destination_tank (str): Destination tank ID
            amount (float): Amount transferred in liters
            success (bool): Whether transfer was successful
        """
        status = "SUCCESS" if success else "FAILED"
        message = f"Transfer {amount}L from {source_tank} to {destination_tank} - {status}"
        severity = "INFO" if success else "WARNING"
        self.log_event("FUEL_TRANSFER", message, source_tank, severity)
    
    def log_alert(self, tank_id, alert_message):
        self.log_event("ALERT", alert_message, tank_id, "WARNING")
    
    def get_logs(self):
        return self._log_entries
    
    def get_logs_by_severity(self, severity):
        return [log for log in self._log_entries if log["severity"] == severity]
    
    def get_logs_by_tank(self, tank_id):
        return [log for log in self._log_entries if log.get("tank_id") == tank_id]
    
    def save_to_file(self):
        try:
            with open(self._log_file_path, 'w') as f:
                json.dump(self._log_entries, f, indent=2)
            print(f"Logs saved to {self._log_file_path}")
            return True
        except Exception as e:
            print(f"Error saving logs: {e}")
            return False
    
    def load_from_file(self):
        try:
            if os.path.exists(self._log_file_path):
                with open(self._log_file_path, 'r') as f:
                    self._log_entries = json.load(f)
                print(f"Loaded {len(self._log_entries)} log entries")
                return True
        except Exception as e:
            print(f"Error loading logs: {e}")
        return False
    
    def clear_logs(self):
        self._log_entries = []
        print("Log entries cleared")
    
    def get_log_count(self):
        return len(self._log_entries)
    
    def __str__(self):
        return f"DataLogger: {len(self._log_entries)} entries logged"
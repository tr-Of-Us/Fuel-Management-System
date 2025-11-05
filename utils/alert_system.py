class AlertSystem:
    """Alert system for monitoring fuel levels and generating warnings"""
    
    def __init__(self, fuel_system, data_logger):
        """
        Initialize alert system.
        
        Args:
            fuel_system: FuelSystem instance
            data_logger: DataLogger instance
        """
        self._fuel_system = fuel_system
        self._logger = data_logger
        self._active_alerts = []
    
    def check_all_tanks(self):
        """
        Check all tanks and generate alerts for issues.
        
        Returns:
            List of active alerts
        """
        self._active_alerts = []
        
        for tank_id, tank in self._fuel_system.get_all_tanks().items():
            # Check fuel level
            status = tank.get_status()
            percentage = tank.get_fuel_percentage()
            
            if status == "CRITICAL":
                alert = {
                    "tank_id": tank_id,
                    "tank_name": tank.get_name(),
                    "severity": "CRITICAL",
                    "type": "FUEL_LEVEL",
                    "message": f"CRITICAL fuel level: {percentage:.1f}%",
                    "value": tank.get_fuel_level()
                }
                self._active_alerts.append(alert)
                self._logger.log_alert(tank_id, alert["message"])
            
            elif status == "LOW":
                alert = {
                    "tank_id": tank_id,
                    "tank_name": tank.get_name(),
                    "severity": "WARNING",
                    "type": "FUEL_LEVEL",
                    "message": f"Low fuel level: {percentage:.1f}%",
                    "value": tank.get_fuel_level()
                }
                self._active_alerts.append(alert)
                self._logger.log_alert(tank_id, alert["message"])
            
            # Check pressure
            pressure = tank.get_pressure()
            max_pressure = tank.get_max_pressure()
            if pressure > max_pressure:
                alert = {
                    "tank_id": tank_id,
                    "tank_name": tank.get_name(),
                    "severity": "WARNING",
                    "type": "PRESSURE",
                    "message": f"Pressure above limit: {pressure:.1f} PSI (max: {max_pressure:.1f})",
                    "value": pressure
                }
                self._active_alerts.append(alert)
                self._logger.log_alert(tank_id, alert["message"])
            
            # Check temperature
            temperature = tank.get_temperature()
            max_temp = tank.get_max_temperature()
            if temperature > max_temp:
                alert = {
                    "tank_id": tank_id,
                    "tank_name": tank.get_name(),
                    "severity": "WARNING",
                    "type": "TEMPERATURE",
                    "message": f"Temperature above limit: {temperature:.1f}°C (max: {max_temp:.1f})",
                    "value": temperature
                }
                self._active_alerts.append(alert)
                self._logger.log_alert(tank_id, alert["message"])
        
        return self._active_alerts
    
    def get_active_alerts(self):
        """Get list of all active alerts"""
        return self._active_alerts
    
    def get_critical_alerts(self):
        """Get only critical severity alerts"""
        return [alert for alert in self._active_alerts if alert["severity"] == "CRITICAL"]
    
    def get_warning_alerts(self):
        """Get only warning severity alerts"""
        return [alert for alert in self._active_alerts if alert["severity"] == "WARNING"]
    
    def get_alerts_by_tank(self, tank_id):
        """Get alerts for specific tank"""
        return [alert for alert in self._active_alerts if alert["tank_id"] == tank_id]
    
    def get_alerts_by_type(self, alert_type):
        """
        Get alerts by type.
        
        Args:
            alert_type: Type of alert (FUEL_LEVEL, PRESSURE, TEMPERATURE)
        """
        return [alert for alert in self._active_alerts if alert["type"] == alert_type]
    
    def has_critical_alerts(self):
        """Check if any critical alerts exist"""
        return len(self.get_critical_alerts()) > 0
    
    def clear_alerts(self):
        """Clear all active alerts"""
        self._active_alerts = []
    
    def get_alert_count(self):
        """Get total number of active alerts"""
        return len(self._active_alerts)
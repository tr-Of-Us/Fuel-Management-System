import sys
sys.path.append('models')
sys.path.append('utils')

from fuel_system import FuelSystem
from fuel_transfer_controller import FuelTransferController
from alert_system import AlertSystem
from data_logger import DataLogger


class SystemIntegration:
    """Integrates all system components"""
    
    def __init__(self):
        """Initialize integrated system"""
        self.logger = DataLogger()
        self.fuel_system = FuelSystem()
        self.transfer_controller = FuelTransferController(self.fuel_system, self.logger)
        self.alert_system = AlertSystem(self.fuel_system, self.logger)
        
        self.logger.log_event("SYSTEM_INIT", "Integrated system initialized")
    
    def add_tank(self, tank):
        """Add tank to system"""
        self.fuel_system.add_tank(tank)
        self.logger.log_event("TANK_ADDED", f"Tank {tank.get_tank_id()} added to system")
    
    def transfer_fuel(self, source_id, dest_id, amount):
        """
        Execute fuel transfer with full logging and alerts.
        
        Returns:
            tuple: (success, message)
        """
        success, message = self.transfer_controller.execute_transfer(source_id, dest_id, amount)
        
        # Check for new alerts after transfer
        if success:
            self.alert_system.check_all_tanks()
        
        return success, message
    
    def get_system_status(self):
        """
        Get comprehensive system status.
        
        Returns:
            Dictionary with system information
        """
        alerts = self.alert_system.check_all_tanks()
        
        return {
            "total_fuel": self.fuel_system.get_total_fuel(),
            "total_capacity": self.fuel_system.get_total_capacity(),
            "fuel_percentage": self.fuel_system.get_system_fuel_percentage(),
            "tank_count": len(self.fuel_system.get_all_tanks()),
            "alert_count": len(alerts),
            "critical_alerts": len(self.alert_system.get_critical_alerts()),
            "low_fuel_tanks": len(self.fuel_system.get_low_fuel_tanks()),
            "status": self.fuel_system.get_system_status()
        }
    
    def export_logs(self):
        """Export system logs to file"""
        return self.logger.save_to_file()
import sys
sys.path.append('models')

from models.main_fuel_tank import MainFuelTank
from models.auxiliary_tank import AuxiliaryTank
from models.reserve_tank import ReserveTank


class FuelSystem:
    """Main fuel system controller - manages all tanks"""
    
    def __init__(self):
        self._tanks = {}
        self._system_status = "INITIALIZING"
    
    def add_tank(self, tank):
        """Add a tank to the system"""
        self._tanks[tank.get_tank_id()] = tank
    
    def get_tank(self, tank_id):
        """Get tank by ID"""
        return self._tanks.get(tank_id)
    
    def get_all_tanks(self):
        """Get all tanks"""
        return self._tanks
    
    def get_tank_ids(self):
        """Get list of all tank IDs"""
        return list(self._tanks.keys())
    
    def get_total_fuel(self):
        """Calculate total fuel across all tanks"""
        return sum(tank.get_fuel_level() for tank in self._tanks.values())
    
    def get_total_capacity(self):
        """Calculate total capacity across all tanks"""
        return sum(tank.get_capacity() for tank in self._tanks.values())
    
    def get_system_fuel_percentage(self):
        """Get overall system fuel percentage"""
        total_capacity = self.get_total_capacity()
        if total_capacity == 0:
            return 0
        return (self.get_total_fuel() / total_capacity) * 100
    
    def get_system_status(self):
        """Get system status"""
        return self._system_status
    
    def set_system_status(self, status):
        """Set system status"""
        self._system_status = status
    
    def get_tanks_by_status(self, status):
        """
        Get tanks with specific status.
        
        Args:
            status: Status to filter by (NORMAL, LOW, CRITICAL)
        
        Returns:
            List of tanks with that status
        """
        return [tank for tank in self._tanks.values() if tank.get_status() == status]
    
    def get_low_fuel_tanks(self):
        """Get list of tanks with low or critical fuel"""
        low_tanks = []
        for tank in self._tanks.values():
            status = tank.get_status()
            if status in ["LOW", "CRITICAL"]:
                low_tanks.append(tank)
        return low_tanks
    
    def check_all_tanks(self):
        """
        Check all tanks and return status summary.
        
        Returns:
            Dictionary with tank statuses
        """
        return {
            tank_id: tank.get_status() 
            for tank_id, tank in self._tanks.items()
        }
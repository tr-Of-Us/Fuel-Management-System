from .fuel_tank import FuelTank

class MainFuelTank(FuelTank):
    """Main fuel tank for primary aircraft fuel storage."""
    
    def __init__(self, tank_id, name, capacity=5000, initial_fuel=0):
        # Initialize main tank with standard capacity
        super().__init__(
            tank_id=tank_id,
            name=name,
            capacity=capacity,
            fuel_type="Jet-A",
            initial_fuel=initial_fuel
        )
        self._tank_type = "MAIN"
    
    def get_tank_type(self):
        return self._tank_type
    
    def check_status(self):
        """Check status: >50% NORMAL, 20-50% LOW, <20% CRITICAL"""
        percentage = self.get_fuel_percentage()
        
        if percentage > 50:
            return "NORMAL"
        elif percentage > 20:
            return "LOW"
        else:
            return "CRITICAL"
    
    def get_low_fuel_threshold(self):
        """Low fuel warning at 20% capacity"""
        return self._capacity * 0.20
    
    def get_critical_fuel_threshold(self):
        """Critical fuel warning at 10% capacity"""
        return self._capacity * 0.10
    
    def __str__(self):
        return (f"[MAIN TANK] {self._name}: "
                f"{self._fuel_level:.1f}L / {self._capacity:.1f}L "
                f"({self.get_fuel_percentage():.1f}%) - {self._status}")
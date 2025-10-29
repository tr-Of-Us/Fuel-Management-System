from fuel_tank import FuelTank

class ReserveTank(FuelTank):

    def __init__(self, tank_id, name, capacity=1000, initial_fuel=0):
        """
        Initialize a reserve fuel tank.
        
        Args:
            tank_id (str): Unique identifier (e.g., "RESERVE")
            name (str): Display name (e.g., "Emergency Reserve Tank")
            capacity (float): Maximum capacity in liters (default: 1000L - smaller than main tanks)
            initial_fuel (float): Starting fuel amount in liters
        """
        super().__init__(
            tank_id=tank_id,
            name=name,
            capacity=capacity,
            fuel_type="Jet-A",
            initial_fuel=initial_fuel
        )
        self._tank_type = "RESERVE"
        self._emergency_mode = False
    
    def get_tank_type(self):
        return self._tank_type
    
    def is_emergency_mode(self):
        return self._emergency_mode
    
    def activate_emergency_mode(self):
        self._emergency_mode = True
        print(f"WARNING: {self._name} emergency mode ACTIVATED")
    
    def deactivate_emergency_mode(self):
        self._emergency_mode = False
        print(f"{self._name} emergency mode deactivated")
    
    def check_status(self):
        """
        Check tank status with stricter thresholds for reserve tanks.
        
        Reserve Tank Thresholds (stricter than main tanks):
        - Above 70%: NORMAL (higher threshold for safety)
        - 30-70%: LOW (earlier warning)
        - Below 30%: CRITICAL (urgent action needed)
        
        Demonstrates polymorphism - different behavior than MainFuelTank/AuxiliaryTank.
        """
        percentage = self.get_fuel_percentage()
        
        if percentage > 70:
            return "NORMAL"
        elif percentage > 30:
            return "LOW"
        else:
            return "CRITICAL"
    
    def get_low_fuel_threshold(self):
        return self._capacity * 0.30
    
    def get_critical_fuel_threshold(self):
        """Critical fuel warning at 15% capacity"""
        return self._capacity * 0.15
    
    def remove_fuel(self, amount):
        if not self._emergency_mode:
            print(f"Error: Cannot access reserve fuel - emergency mode not activated")
            return False
        
        # Call parent class method if emergency mode is active
        return super().remove_fuel(amount)
    
    def __str__(self):
        emergency_status = " [EMERGENCY MODE]" if self._emergency_mode else ""
        return (f"[RESERVE] {self._name}: "
                f"{self._fuel_level:.1f}L / {self._capacity:.1f}L "
                f"({self.get_fuel_percentage():.1f}%) - {self._status}{emergency_status}")
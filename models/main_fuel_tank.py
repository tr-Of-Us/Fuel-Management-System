from fuel_tank import FuelTank

class MainFuelTank(FuelTank):
    """
    Main fuel tank class for primary aircraft fuel storage.
    
    Main tanks are the primary fuel source and have standard warning thresholds.
    Typically located in the wings of the aircraft.
    """
    
    def __init__(self, tank_id, name, capacity=5000, initial_fuel=0):
        """
        Initialize a main fuel tank.
        
        Args:
            tank_id (str): Unique identifier (e.g., "LEFT_MAIN", "RIGHT_MAIN")
            name (str): Display name (e.g., "Left Wing Main Tank")
            capacity (float): Maximum capacity in liters (default: 5000L)
            initial_fuel (float): Starting fuel amount in liters
        """
        # Call parent class constructor
        super().__init__(
            tank_id=tank_id,
            name=name,
            capacity=capacity,
            fuel_type="Jet-A",
            initial_fuel=initial_fuel
        )
        
        # Main tank specific attributes
        self._tank_type = "MAIN"
    
    def get_tank_type(self):
        """Return the tank type"""
        return self._tank_type
    
    # Override abstract method (Polymorphism)
    def check_status(self):
        """
        Check tank status based on fuel percentage.
        
        Main Tank Thresholds:
        - Above 50%: NORMAL
        - 20-50%: LOW
        - Below 20%: CRITICAL
        
        Returns:
            str: Status ("NORMAL", "LOW", "CRITICAL")
        """
        percentage = self.get_fuel_percentage()
        
        if percentage > 50:
            return "NORMAL"
        elif percentage > 20:
            return "LOW"
        else:
            return "CRITICAL"
    
    # Override abstract method (Polymorphism)
    def get_low_fuel_threshold(self):
        """
        Get the low fuel warning threshold for main tanks.
        
        Returns:
            float: 20% of capacity
        """
        return self._capacity * 0.20
    
    def get_critical_fuel_threshold(self):
        """
        Get the critical fuel threshold.
        
        Returns:
            float: 10% of capacity
        """
        return self._capacity * 0.10
    
    def __str__(self):
        """String representation"""
        return (f"[MAIN TANK] {self._name}: "
                f"{self._fuel_level:.1f}L / {self._capacity:.1f}L "
                f"({self.get_fuel_percentage():.1f}%) - {self._status}")
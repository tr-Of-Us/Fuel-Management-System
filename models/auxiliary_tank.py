from fuel_tank import FuelTank

class AuxiliaryTank(FuelTank):
    
    def __init__(self, tank_id, name, capacity=3000, initial_fuel=0):
        """
        Initialize an auxiliary fuel tank.
        
        Args:
            tank_id (str): Unique identifier (e.g., "CENTER_AUX")
            name (str): Display name (e.g., "Center Auxiliary Tank")
            capacity (float): Maximum capacity in liters (default: 3000L)
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
        
        # Auxiliary tank specific attributes
        self._tank_type = "AUXILIARY"
    
    def get_tank_type(self):
        """Return the tank type"""
        return self._tank_type
    
    # Override abstract method 
    def check_status(self):
        """
        Check tank status based on fuel percentage.
        
        Auxiliary Tank Thresholds (similar to main tanks):
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
    
    # Override abstract method 
    def get_low_fuel_threshold(self):
        """
        Get the low fuel warning threshold for auxiliary tanks.
        
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
    
    def is_available_for_transfer(self):
        """
        Check if tank has sufficient fuel for transfer operations.
        Auxiliary tanks should maintain minimum reserves.
        
        Returns:
            bool: True if enough fuel for transfer
        """
        return self._fuel_level > self.get_low_fuel_threshold()
    
    def __str__(self):
        """String representation"""
        return (f"[AUXILIARY] {self._name}: "
                f"{self._fuel_level:.1f}L / {self._capacity:.1f}L "
                f"({self.get_fuel_percentage():.1f}%) - {self._status}")
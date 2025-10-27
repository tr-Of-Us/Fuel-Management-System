from abc import ABC, abstractmethod

class FuelTank(ABC):
    """
    Abstract base class representing a fuel tank.
    
    This class cannot be instantiated directly - it must be inherited
    by concrete tank classes (MainFuelTank, AuxiliaryTank, ReserveTank).
    """
    
    def __init__(self, tank_id, name, capacity, fuel_type="Jet-A", initial_fuel=0):
        """
        Initialize a fuel tank.
        
        Args:
            tank_id (str): Unique identifier (e.g., "LEFT_MAIN")
            name (str): Display name (e.g., "Left Wing Main Tank")
            capacity (float): Maximum fuel capacity in liters
            fuel_type (str): Type of fuel (default: Jet-A)
            initial_fuel (float): Starting fuel amount in liters
        """
        # Private attributes (encapsulation)
        self._tank_id = tank_id
        self._name = name
        self._capacity = capacity
        self._fuel_type = fuel_type
        self._fuel_level = min(initial_fuel, capacity)  # Don't exceed capacity
        self._pressure = 45.0  # PSI (pounds per square inch)
        self._temperature = 25.0  # Celsius
        self._status = "NORMAL"
        
        # Maximum safe limits
        self._max_pressure = 50.0  # PSI 
        self._max_temperature = 60.0  # Celsius
    
    # getters (Encapsulation) 
    
    def get_tank_id(self):
        """Return the tank's unique identifier"""
        return self._tank_id
    
    def get_name(self):
        """Return the tank's display name"""
        return self._name
    
    def get_capacity(self):
        """Return maximum fuel capacity in liters"""
        return self._capacity
    
    def get_fuel_type(self):
        """Return the type of fuel in the tank"""
        return self._fuel_type
    
    def get_fuel_level(self):
        """Return current fuel level in liters"""
        return self._fuel_level
    
    def get_fuel_percentage(self):
        """
        Return fuel level as percentage of capacity.
        
        Returns:
            float: Percentage (0-100)
        """
        if self._capacity == 0:
            return 0
        return (self._fuel_level / self._capacity) * 100
    
    def get_pressure(self):
        """Return current pressure in PSI"""
        return self._pressure
    
    def get_temperature(self):
        """Return current temperature in Celsius"""
        return self._temperature
    
    def get_status(self):
        """Return current tank status (NORMAL, LOW, CRITICAL)"""
        return self._status
    
    def get_max_pressure(self):
        """Return maximum safe pressure limit"""
        return self._max_pressure
    
    def get_max_temperature(self):
        """Return maximum safe temperature limit"""
        return self._max_temperature
    
    # setters (Encapsulation) 
    
    def set_pressure(self, pressure):
        """
        Set current pressure with validation.
        
        Args:
            pressure (float): Pressure in PSI
            
        Returns:
            bool: True if successful, False if invalid
        """
        if pressure < 0:
            print(f"Error: Pressure cannot be negative")
            return False
        if pressure > self._max_pressure * 1.2:  # 20% over max is dangerous
            print(f"Error: Pressure {pressure} PSI exceeds safe limit")
            return False
        
        self._pressure = pressure
        return True
    
    def set_temperature(self, temperature):
        """
        Set current temperature with validation.
        
        Args:
            temperature (float): Temperature in Celsius
            
        Returns:
            bool: True if successful, False if invalid
        """
        if temperature < -50:  # Fuel freezes at very low temps
            print(f"Error: Temperature too low for fuel operation")
            return False
        if temperature > self._max_temperature * 1.2:
            print(f"Error: Temperature {temperature}°C exceeds safe limit")
            return False
        
        self._temperature = temperature
        return True
    
    # Fuel Management Methods
    
    def add_fuel(self, amount):
        """
        Add fuel to the tank with overflow protection.
        
        Args:
            amount (float): Amount of fuel to add in liters
            
        Returns:
            bool: True if successful, False if would overflow
        """
        if amount < 0:
            print(f"Error: Cannot add negative fuel amount")
            return False
        
        if self._fuel_level + amount > self._capacity:
            available = self._capacity - self._fuel_level
            print(f"Error: Cannot add {amount}L - only {available:.1f}L space available")
            return False
        
        self._fuel_level += amount
        self._update_status()
        return True
    
    def remove_fuel(self, amount):
        """
        Remove fuel from the tank with validation.
        
        Args:
            amount (float): Amount of fuel to remove in liters
            
        Returns:
            bool: True if successful, False if insufficient fuel
        """
        if amount < 0:
            print(f"Error: Cannot remove negative fuel amount")
            return False
        
        if self._fuel_level < amount:
            print(f"Error: Insufficient fuel - only {self._fuel_level:.1f}L available")
            return False
        
        self._fuel_level -= amount
        self._update_status()
        return True
    
    def get_available_capacity(self):
        """
        Get remaining space available for fuel.
        
        Returns:
            float: Available capacity in liters
        """
        return self._capacity - self._fuel_level
    
    def is_empty(self):
        """Check if tank is empty"""
        return self._fuel_level <= 0
    
    def is_full(self):
        """Check if tank is full (within 99% capacity)"""
        return self._fuel_level >= self._capacity * 0.99
    
    # Abstraction
    
    @abstractmethod
    def check_status(self):
        """
        Check and return tank status based on fuel level.
        
        Different tank types have different warning thresholds:
        - MainFuelTank: Standard thresholds
        - AuxiliaryTank: Similar to main tanks
        - ReserveTank: Stricter warnings (polymorphism)
        
        Returns:
            str: Status string ("NORMAL", "LOW", "CRITICAL")
        """
        pass
    
    @abstractmethod
    def get_low_fuel_threshold(self):
        """
        Get the fuel level that triggers low fuel warning.
        
        Different tank types have different thresholds (polymorphism).
        
        Returns:
            float: Fuel level in liters that triggers warning
        """
        pass
    
    # Helper methods
    
    def _update_status(self):
        """
        Update tank status based on current fuel level.
        Called internally after fuel changes.
        """
        self._status = self.check_status()
    
    # Data export for Json
    
    def to_dict(self):
        """
        Convert tank data to dictionary for JSON serialization.
        
        Returns:
            dict: Dictionary containing all tank data
        """
        return {
            "tank_id": self._tank_id,
            "name": self._name,
            "capacity": self._capacity,
            "fuel_type": self._fuel_type,
            "fuel_level": self._fuel_level,
            "fuel_percentage": self.get_fuel_percentage(),
            "pressure": self._pressure,
            "temperature": self._temperature,
            "status": self._status,
            "max_pressure": self._max_pressure,
            "max_temperature": self._max_temperature
        }
    
    # String Representations  
    
    def __str__(self):
        """
        String representation for printing.
        
        Returns:
            str: Formatted tank information
        """
        return (f"{self._name} ({self._tank_id}): "
                f"{self._fuel_level:.1f}L / {self._capacity:.1f}L "
                f"({self.get_fuel_percentage():.1f}%) - {self._status}")
    
    def __repr__(self):
        """
        Developer-friendly representation.
        
        Returns:
            str: Technical representation
        """
        return f"FuelTank(id={self._tank_id}, fuel={self._fuel_level}/{self._capacity})"
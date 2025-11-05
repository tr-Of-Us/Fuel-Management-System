from abc import ABC, abstractmethod

class FuelTank(ABC):
    
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
    
    # setters 
    def set_pressure(self, pressure):
        """Set pressure with validation (0 to 120% of max)"""
        if pressure < 0:
            print(f"Error: Pressure cannot be negative")
            return False
        if pressure > self._max_pressure * 1.2:
            print(f"Error: Pressure {pressure} PSI exceeds safe limit")
            return False
        self._pressure = pressure
        return True
    
    def set_temperature(self, temperature):
        """Set temperature with validation (-50°C to 120% of max)"""
        if temperature < -50:
            print(f"Error: Temperature too low for fuel operation")
            return False
        if temperature > self._max_temperature * 1.2:
            print(f"Error: Temperature {temperature}°C exceeds safe limit")
            return False
        self._temperature = temperature
        return True
    
    # Fuel management methods
    def add_fuel(self, amount):
        """Add fuel with overflow protection"""
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
        """Remove fuel with validation"""
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
        """Return remaining space in tank"""
        return self._capacity - self._fuel_level
    
    def is_empty(self):
        return self._fuel_level <= 0
    
    def is_full(self):
        """Check if tank is full (99% or more)"""
        return self._fuel_level >= self._capacity * 0.99
    
    @abstractmethod
    def check_status(self):
        """Return tank status based on fuel level (NORMAL/LOW/CRITICAL)"""
        pass
    
    @abstractmethod
    def get_low_fuel_threshold(self):
        """Return fuel level that triggers low fuel warning"""
        pass
    
    def _update_status(self):
        """Update tank status after fuel changes"""
        self._status = self.check_status()
    
    def to_dict(self):
        """Convert tank data to dictionary for JSON export"""
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
    
    def __str__(self):
        return (f"{self._name} ({self._tank_id}): "
                f"{self._fuel_level:.1f}L / {self._capacity:.1f}L "
                f"({self.get_fuel_percentage():.1f}%) - {self._status}")
    
    def __repr__(self):
        return f"FuelTank(id={self._tank_id}, fuel={self._fuel_level}/{self._capacity})"
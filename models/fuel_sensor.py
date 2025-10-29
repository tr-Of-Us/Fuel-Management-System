class FuelSensor:
    
    def __init__(self, sensor_id, sensor_type, tank_id):
        """
        Initialize a fuel sensor.
        
        Args:
            sensor_id (str): Unique sensor identifier (e.g., "SENSOR_001")
            sensor_type (str): Type of sensor ("LEVEL", "PRESSURE", "TEMPERATURE")
            tank_id (str): ID of the tank this sensor monitors
        """
        # Private attributes (encapsulation)
        self._sensor_id = sensor_id
        self._sensor_type = sensor_type
        self._tank_id = tank_id
        self._current_reading = 0.0
        self._calibration_offset = 0.0
        self._is_operational = True
    
    # Getters
    def get_sensor_id(self):
        return self._sensor_id
    
    def get_sensor_type(self):
        return self._sensor_type
    
    def get_tank_id(self):
        return self._tank_id
    
    def get_reading(self):
        if not self._is_operational:
            return None
        return self._current_reading + self._calibration_offset
    
    def is_operational(self):
        return self._is_operational
    
    # Setters
    def set_reading(self, value):
        self._current_reading = value
    
    def calibrate(self, offset):
        """
        Set calibration offset for sensor accuracy.
        
        Args:
            offset (float): Calibration adjustment value
        """
        self._calibration_offset = offset
        print(f"Sensor {self._sensor_id} calibrated with offset: {offset}")
    
    def set_operational_status(self, status):
        self._is_operational = status
        if not status:
            print(f"WARNING: Sensor {self._sensor_id} marked as non-operational")
    
    def perform_self_test(self):
        # Simple validation - check if reading is within reasonable bounds
        if self._sensor_type == "LEVEL":
            # Fuel level should be 0-100% or 0-capacity liters
            is_valid = 0 <= self._current_reading <= 10000
        elif self._sensor_type == "PRESSURE":
            # Pressure typically 0-100 PSI
            is_valid = 0 <= self._current_reading <= 100
        elif self._sensor_type == "TEMPERATURE":
            # Temperature typically -50 to 100°C
            is_valid = -50 <= self._current_reading <= 100
        else:
            is_valid = True
        
        self._is_operational = is_valid
        return is_valid
    
    def to_dict(self):
        """Convert sensor data to dictionary for JSON export"""
        return {
            "sensor_id": self._sensor_id,
            "sensor_type": self._sensor_type,
            "tank_id": self._tank_id,
            "current_reading": self._current_reading,
            "calibration_offset": self._calibration_offset,
            "operational": self._is_operational,
            "calibrated_reading": self.get_reading()
        }
    
    def __str__(self):
        status = "OPERATIONAL" if self._is_operational else "FAULT"
        reading = self.get_reading()
        return f"Sensor {self._sensor_id} ({self._sensor_type}) - Tank: {self._tank_id} - Reading: {reading} [{status}]"
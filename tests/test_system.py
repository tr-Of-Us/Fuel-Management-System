import unittest
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.fuel_tank import FuelTank
from models.main_fuel_tank import MainFuelTank
from models.auxiliary_tank import AuxiliaryTank
from models.reserve_tank import ReserveTank
from models.fuel_sensor import FuelSensor
from utils.data_logger import DataLogger

class TestFuelTanks(unittest.TestCase):
    """Test cases for fuel tank classes"""
    
    def test_main_tank_creation(self):
        tank = MainFuelTank("LEFT_MAIN", "Left Wing Main Tank", 5000, 4500)
        self.assertEqual(tank.get_tank_id(), "LEFT_MAIN")
        self.assertEqual(tank.get_capacity(), 5000)
        self.assertEqual(tank.get_fuel_level(), 4500)
        self.assertEqual(tank.get_tank_type(), "MAIN")
    
    def test_auxiliary_tank_creation(self):
        tank = AuxiliaryTank("CENTER_AUX", "Center Auxiliary Tank", 3000, 2500)
        self.assertEqual(tank.get_tank_id(), "CENTER_AUX")
        self.assertEqual(tank.get_capacity(), 3000)
        self.assertEqual(tank.get_tank_type(), "AUXILIARY")
    
    def test_reserve_tank_creation(self):
        tank = ReserveTank("RESERVE", "Emergency Reserve Tank", 1000, 1000)
        self.assertEqual(tank.get_tank_id(), "RESERVE")
        self.assertEqual(tank.get_tank_type(), "RESERVE")
        self.assertFalse(tank.is_emergency_mode())
    
    def test_add_fuel_normal(self):
        tank = MainFuelTank("TEST", "Test Tank", 5000, 3000)
        result = tank.add_fuel(500)
        self.assertTrue(result)
        self.assertEqual(tank.get_fuel_level(), 3500)
    
    def test_add_fuel_overflow(self):
        tank = MainFuelTank("TEST", "Test Tank", 5000, 4800)
        result = tank.add_fuel(500)  # Would exceed capacity
        self.assertFalse(result)
        self.assertEqual(tank.get_fuel_level(), 4800)  # Unchanged
    
    def test_remove_fuel_normal(self):
        tank = MainFuelTank("TEST", "Test Tank", 5000, 3000)
        result = tank.remove_fuel(500)
        self.assertTrue(result)
        self.assertEqual(tank.get_fuel_level(), 2500)
    
    def test_remove_fuel_insufficient(self):
        tank = MainFuelTank("TEST", "Test Tank", 5000, 300)
        result = tank.remove_fuel(500)  # Not enough fuel
        self.assertFalse(result)
        self.assertEqual(tank.get_fuel_level(), 300)  # Unchanged
    
    def test_fuel_percentage_calculation(self):
        tank = MainFuelTank("TEST", "Test Tank", 5000, 2500)
        self.assertEqual(tank.get_fuel_percentage(), 50.0)
    
    def test_main_tank_status_normal(self):
        tank = MainFuelTank("TEST", "Test Tank", 5000, 4000)
        self.assertEqual(tank.check_status(), "NORMAL")  # 80% > 50%
    
    def test_main_tank_status_low(self):
        tank = MainFuelTank("TEST", "Test Tank", 5000, 1500)
        self.assertEqual(tank.check_status(), "LOW")  # 30% between 20-50%
    
    def test_main_tank_status_critical(self):
        tank = MainFuelTank("TEST", "Test Tank", 5000, 500)
        self.assertEqual(tank.check_status(), "CRITICAL")  # 10% < 20%
    
    def test_reserve_tank_status_thresholds(self):
        tank = ReserveTank("TEST", "Test Reserve", 1000, 600)
        self.assertEqual(tank.check_status(), "LOW")
    
    def test_reserve_tank_emergency_mode(self):
        tank = ReserveTank("TEST", "Test Reserve", 1000, 500)
        # Cannot remove fuel without emergency mode
        result = tank.remove_fuel(100)
        self.assertFalse(result)
        self.assertEqual(tank.get_fuel_level(), 500)
        
        # Activate emergency mode
        tank.activate_emergency_mode()
        result = tank.remove_fuel(100)
        self.assertTrue(result)
        self.assertEqual(tank.get_fuel_level(), 400)
    
    def test_pressure_validation(self):
        tank = MainFuelTank("TEST", "Test Tank", 5000, 3000)
        # Valid pressure
        self.assertTrue(tank.set_pressure(45.0))
        self.assertEqual(tank.get_pressure(), 45.0)
        # Invalid negative pressure
        self.assertFalse(tank.set_pressure(-10.0))
    
    def test_temperature_validation(self):
        tank = MainFuelTank("TEST", "Test Tank", 5000, 3000)
        # Valid temperature
        self.assertTrue(tank.set_temperature(30.0))
        self.assertEqual(tank.get_temperature(), 30.0)
        # Invalid low temperature
        self.assertFalse(tank.set_temperature(-60.0))


class TestFuelSensor(unittest.TestCase):
    
    def test_sensor_creation(self):
        sensor = FuelSensor("SENS_001", "LEVEL", "LEFT_MAIN")
        self.assertEqual(sensor.get_sensor_id(), "SENS_001")
        self.assertEqual(sensor.get_sensor_type(), "LEVEL")
        self.assertEqual(sensor.get_tank_id(), "LEFT_MAIN")
        self.assertTrue(sensor.is_operational())
    
    def test_sensor_reading(self):
        sensor = FuelSensor("SENS_001", "LEVEL", "LEFT_MAIN")
        sensor.set_reading(4500.0)
        self.assertEqual(sensor.get_reading(), 4500.0)
    
    def test_sensor_calibration(self):
        sensor = FuelSensor("SENS_001", "PRESSURE", "LEFT_MAIN")
        sensor.set_reading(45.0)
        sensor.calibrate(2.5)  # Add calibration offset
        self.assertEqual(sensor.get_reading(), 47.5)
    
    def test_sensor_self_test(self):
        sensor = FuelSensor("SENS_001", "LEVEL", "LEFT_MAIN")
        sensor.set_reading(4500.0)
        self.assertTrue(sensor.perform_self_test())
        
        # Invalid reading
        sensor.set_reading(20000.0)  # Way too high
        self.assertFalse(sensor.perform_self_test())
        self.assertFalse(sensor.is_operational())


class TestDataLogger(unittest.TestCase):
    
    def test_logger_creation(self):
        logger = DataLogger("data/logs/test_log.json")
        self.assertEqual(logger.get_log_count(), 0)
    
    def test_log_event(self):
        logger = DataLogger("data/logs/test_log.json")
        logger.log_event("TEST_EVENT", "This is a test", "TEST_TANK", "INFO")
        self.assertEqual(logger.get_log_count(), 1)
    
    def test_log_fuel_level(self):
        logger = DataLogger("data/logs/test_log.json")
        logger.log_fuel_level("LEFT_MAIN", 4500, 5000, 90.0)
        logs = logger.get_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["event_type"], "FUEL_LEVEL")
    
    def test_log_filtering_by_severity(self):
        logger = DataLogger("data/logs/test_log.json")
        logger.log_event("EVENT1", "Info message", severity="INFO")
        logger.log_event("EVENT2", "Warning message", severity="WARNING")
        logger.log_event("EVENT3", "Critical message", severity="CRITICAL")
        
        warnings = logger.get_logs_by_severity("WARNING")
        self.assertEqual(len(warnings), 1)
        self.assertEqual(warnings[0]["severity"], "WARNING")


if __name__ == "__main__":
    unittest.main()
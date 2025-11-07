import unittest
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
sys.path.append('models')
sys.path.append('controllers')
sys.path.append('utils')

from fuel_system import FuelSystem
from fuel_transfer_controller import FuelTransferController
from utils.alert_system import AlertSystem
from utils.system_integration import SystemIntegration
from utils.validation import *
from utils.data_logger import DataLogger
from models.main_fuel_tank import MainFuelTank
from models.auxiliary_tank import AuxiliaryTank
from models.reserve_tank import ReserveTank


class TestFuelSystem(unittest.TestCase):
    
    def setUp(self):
        self.system = FuelSystem()
        self.tank1 = MainFuelTank("T1", "Tank 1", 5000, 4000)
        self.tank2 = AuxiliaryTank("T2", "Tank 2", 3000, 2000)
        self.system.add_tank(self.tank1)
        self.system.add_tank(self.tank2)
    
    def test_add_tank(self):
        """Test ID: C01"""
        tank3 = ReserveTank("T3", "Tank 3", 1000, 1000)
        self.system.add_tank(tank3)
        self.assertEqual(len(self.system.get_all_tanks()), 3)
    
    def test_get_tank(self):
        """Test ID: C02"""
        tank = self.system.get_tank("T1")
        self.assertIsNotNone(tank)
        self.assertEqual(tank.get_tank_id(), "T1")
    
    def test_get_tank_ids(self):
        """Test ID: C03"""
        ids = self.system.get_tank_ids()
        self.assertEqual(len(ids), 2)
        self.assertIn("T1", ids)
        self.assertIn("T2", ids)
    
    def test_get_total_fuel(self):
        """Test ID: C04"""
        total = self.system.get_total_fuel()
        self.assertEqual(total, 6000)
    
    def test_get_total_capacity(self):
        """Test ID: C05"""
        total = self.system.get_total_capacity()
        self.assertEqual(total, 8000)
    
    def test_get_system_fuel_percentage(self):
        """Test ID: C06"""
        percentage = self.system.get_system_fuel_percentage()
        self.assertEqual(percentage, 75.0)
    
    def test_get_tanks_by_status(self):
        """Test ID: C07"""
        normal_tanks = self.system.get_tanks_by_status("NORMAL")
        self.assertEqual(len(normal_tanks), 2)
    
    def test_get_low_fuel_tanks(self):
        """Test ID: C08"""
        low_tank = MainFuelTank("LOW", "Low Tank", 5000, 500)
        low_tank._status = low_tank.check_status()
        self.system.add_tank(low_tank)
        low_tanks = self.system.get_low_fuel_tanks()
        self.assertGreater(len(low_tanks), 0)
    
    def test_check_all_tanks(self):
        """Test ID: C09"""
        statuses = self.system.check_all_tanks()
        self.assertEqual(len(statuses), 2)
        self.assertIn("T1", statuses)


class TestFuelTransferController(unittest.TestCase):
    
    def setUp(self):
        self.system = FuelSystem()
        self.logger = DataLogger()
        self.controller = FuelTransferController(self.system, self.logger)
        
        self.tank1 = MainFuelTank("SRC", "Source", 5000, 4000)
        self.tank2 = AuxiliaryTank("DST", "Destination", 3000, 1000)
        self.system.add_tank(self.tank1)
        self.system.add_tank(self.tank2)
    
    def test_validate_transfer_success(self):
        """Test ID: C10"""
        valid, msg = self.controller.validate_transfer("SRC", "DST", 500)
        self.assertTrue(valid)
    
    def test_validate_same_tank(self):
        """Test ID: C11"""
        valid, msg = self.controller.validate_transfer("SRC", "SRC", 500)
        self.assertFalse(valid)
        self.assertIn("different", msg.lower())
    
    def test_validate_insufficient_fuel(self):
        """Test ID: C12"""
        valid, msg = self.controller.validate_transfer("SRC", "DST", 5000)
        self.assertFalse(valid)
        self.assertIn("insufficient fuel", msg.lower())
    
    def test_validate_insufficient_capacity(self):
        """Test ID: C13"""
        valid, msg = self.controller.validate_transfer("SRC", "DST", 3000)
        self.assertFalse(valid)
        self.assertIn("insufficient capacity", msg.lower())
    
    def test_validate_negative_amount(self):
        """Test ID: C14"""
        valid, msg = self.controller.validate_transfer("SRC", "DST", -100)
        self.assertFalse(valid)
        self.assertIn("positive", msg.lower())
    
    def test_execute_transfer_success(self):
        """Test ID: C15"""
        initial_src = self.tank1.get_fuel_level()
        initial_dst = self.tank2.get_fuel_level()
        
        success, msg = self.controller.execute_transfer("SRC", "DST", 500)
        
        self.assertTrue(success)
        self.assertEqual(self.tank1.get_fuel_level(), initial_src - 500)
        self.assertEqual(self.tank2.get_fuel_level(), initial_dst + 500)
    
    def test_execute_transfer_invalid(self):
        """Test ID: C16"""
        success, msg = self.controller.execute_transfer("SRC", "DST", -100)
        self.assertFalse(success)
    
    def test_reserve_tank_validation(self):
        """Test ID: C17"""
        reserve = ReserveTank("RES", "Reserve", 1000, 1000)
        self.system.add_tank(reserve)
        
        valid, msg = self.controller.validate_transfer("RES", "DST", 100)
        self.assertFalse(valid)
        self.assertIn("emergency", msg.lower())
    
    def test_reserve_tank_with_emergency_mode(self):
        """Test ID: C18"""
        reserve = ReserveTank("RES", "Reserve", 1000, 1000)
        self.system.add_tank(reserve)
        reserve.activate_emergency_mode()
        
        valid, msg = self.controller.validate_transfer("RES", "DST", 100)
        self.assertTrue(valid)

class TestAlertSystem(unittest.TestCase):
    
    def setUp(self):
        self.system = FuelSystem()
        self.logger = DataLogger()
        self.alert_system = AlertSystem(self.system, self.logger)
        
        self.normal = MainFuelTank("NORM", "Normal", 5000, 4500)
        self.low = MainFuelTank("LOW", "Low", 5000, 1000)
        self.critical = MainFuelTank("CRIT", "Critical", 5000, 200)
        
        self.normal._status = self.normal.check_status()
        self.low._status = self.low.check_status()
        self.critical._status = self.critical.check_status()
        
        self.system.add_tank(self.normal)
        self.system.add_tank(self.low)
        self.system.add_tank(self.critical)
    
    def test_check_all_tanks(self):
        """Test ID: C19"""
        alerts = self.alert_system.check_all_tanks()
        self.assertGreater(len(alerts), 0)
    
    def test_get_critical_alerts(self):
        """Test ID: C20"""
        self.alert_system.check_all_tanks()
        critical = self.alert_system.get_critical_alerts()
        self.assertGreaterEqual(len(critical), 1)
        # Verify CRIT tank is in the alerts
        crit_ids = [a['tank_id'] for a in critical]
        self.assertIn("CRIT", crit_ids)
    
    def test_get_warning_alerts(self):
        """Test ID: C21"""
        self.alert_system.check_all_tanks()
        all_alerts = self.alert_system.get_active_alerts()
        self.assertGreater(len(all_alerts), 0)
    
    def test_get_alerts_by_tank(self):
        """Test ID: C22"""
        self.alert_system.check_all_tanks()
        alerts = self.alert_system.get_alerts_by_tank("LOW")
        self.assertGreaterEqual(len(alerts), 1)
    
    def test_get_alerts_by_type(self):
        """Test ID: C23"""
        self.alert_system.check_all_tanks()
        fuel_alerts = self.alert_system.get_alerts_by_type("FUEL_LEVEL")
        self.assertGreaterEqual(len(fuel_alerts), 1)
    
    def test_has_critical_alerts(self):
        """Test ID: C24"""
        self.alert_system.check_all_tanks()
        self.assertTrue(self.alert_system.has_critical_alerts())
    
    def test_clear_alerts(self):
        """Test ID: C25"""
        self.alert_system.check_all_tanks()
        self.alert_system.clear_alerts()
        self.assertEqual(self.alert_system.get_alert_count(), 0)
    
    def test_pressure_alert(self):
        """Test ID: C26"""
        self.normal.set_pressure(60)  # Above max
        self.alert_system.check_all_tanks()
        pressure_alerts = self.alert_system.get_alerts_by_type("PRESSURE")
        self.assertEqual(len(pressure_alerts), 1)
    
    def test_temperature_alert(self):
        """Test ID: C27"""
        self.normal.set_temperature(70)  # Above max
        self.alert_system.check_all_tanks()
        temp_alerts = self.alert_system.get_alerts_by_type("TEMPERATURE")
        self.assertEqual(len(temp_alerts), 1)


class TestValidation(unittest.TestCase):
    
    def test_validate_fuel_amount_valid(self):
        """Test ID: C28"""
        valid, msg = validate_fuel_amount(500)
        self.assertTrue(valid)
    
    def test_validate_fuel_amount_negative(self):
        """Test ID: C29"""
        valid, msg = validate_fuel_amount(-100)
        self.assertFalse(valid)
    
    def test_validate_fuel_amount_invalid(self):
        """Test ID: C30"""
        valid, msg = validate_fuel_amount("abc")
        self.assertFalse(valid)
    
    def test_validate_tank_id_valid(self):
        """Test ID: C31"""
        valid, msg = validate_tank_id("TANK_01")
        self.assertTrue(valid)
    
    def test_validate_tank_id_empty(self):
        """Test ID: C32"""
        valid, msg = validate_tank_id("")
        self.assertFalse(valid)
    
    def test_validate_capacity_valid(self):
        """Test ID: C33"""
        valid, msg = validate_tank_capacity(5000)
        self.assertTrue(valid)
    
    def test_validate_capacity_negative(self):
        """Test ID: C34"""
        valid, msg = validate_tank_capacity(-100)
        self.assertFalse(valid)
    
    def test_validate_pressure_safe(self):
        """Test ID: C35"""
        safe, msg = validate_pressure(45, 50)
        self.assertTrue(safe)
    
    def test_validate_pressure_unsafe(self):
        """Test ID: C36"""
        safe, msg = validate_pressure(55, 50)
        self.assertFalse(safe)
    
    def test_validate_temperature_safe(self):
        """Test ID: C37"""
        safe, msg = validate_temperature(50, 60)
        self.assertTrue(safe)
    
    def test_validate_temperature_unsafe(self):
        """Test ID: C38"""
        safe, msg = validate_temperature(65, 60)
        self.assertFalse(safe)
    
    def test_format_fuel_amount(self):
        """Test ID: C39"""
        formatted = format_fuel_amount(1234.567)
        self.assertEqual(formatted, "1234.6L")
    
    def test_format_percentage(self):
        """Test ID: C40"""
        formatted = format_percentage(89.234)
        self.assertEqual(formatted, "89.2%")
    
    def test_sanitize_tank_name(self):
        """Test ID: C41"""
        sanitized = sanitize_tank_name("  Left   Wing  ")
        self.assertEqual(sanitized, "Left Wing")

class TestSystemIntegration(unittest.TestCase):
    """Test SystemIntegration"""
    
    def setUp(self):
        self.integration = SystemIntegration()
        
        self.tank1 = MainFuelTank("T1", "Tank 1", 5000, 4000)
        self.tank2 = AuxiliaryTank("T2", "Tank 2", 3000, 2000)
        
        self.integration.add_tank(self.tank1)
        self.integration.add_tank(self.tank2)
    
    def test_add_tank(self):
        """Test ID: C42"""
        tank3 = ReserveTank("T3", "Tank 3", 1000, 1000)
        self.integration.add_tank(tank3)
        self.assertEqual(len(self.integration.fuel_system.get_all_tanks()), 3)
    
    def test_transfer_fuel(self):
        """Test ID: C43"""
        success, msg = self.integration.transfer_fuel("T1", "T2", 500)
        self.assertTrue(success)
        self.assertEqual(self.tank1.get_fuel_level(), 3500)
        self.assertEqual(self.tank2.get_fuel_level(), 2500)
    
    def test_get_system_status(self):
        """Test ID: C44"""
        status = self.integration.get_system_status()
        
        self.assertIn('total_fuel', status)
        self.assertIn('total_capacity', status)
        self.assertIn('fuel_percentage', status)
        self.assertIn('tank_count', status)
        self.assertIn('alert_count', status)
        
        self.assertEqual(status['tank_count'], 2)
        self.assertEqual(status['total_fuel'], 6000)
        self.assertEqual(status['total_capacity'], 8000)


if __name__ == "__main__":
    # Run tests with verbosity
    unittest.main(verbosity=2)
import unittest
import sys
import os
import tkinter as tk

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from gui.main_window import FuelManagementGUI

class TestGUIBasic(unittest.TestCase):
    
    def setUp(self):
        self.root = tk.Tk()
        self.root.withdraw()  
        self.app = FuelManagementGUI(self.root)
    
    def tearDown(self):
        try:
            self.root.destroy()
        except:
            pass
    
    def test_gui_initialization(self):
        """Test ID: GUI-01"""
        self.assertIsNotNone(self.app.root)
        self.assertEqual(self.app.root.title(), "Aerospace Fuel Management System")
        self.assertGreater(len(self.app.fuel_system.get_tank_ids()), 0)
    
    def test_transfer_validation_same_tank(self):
        """Test ID: GUI-02"""
        tank_ids = self.app.fuel_system.get_tank_ids()
        if len(tank_ids) > 0:
            self.app.source_var.set(tank_ids[0])
            self.app.dest_var.set(tank_ids[0])
            self.app.amount_var.set("500")
            
            self.app.initiate_transfer()
            status = self.app.transfer_status_label.cget("text")
            self.assertIn("different", status.lower())
    
    def test_transfer_validation_negative_amount(self):
        """Test ID: GUI-03"""
        tank_ids = self.app.fuel_system.get_tank_ids()
        if len(tank_ids) >= 2:
            self.app.source_var.set(tank_ids[0])
            self.app.dest_var.set(tank_ids[1])
            self.app.amount_var.set("-100")
            
            self.app.initiate_transfer()
            status = self.app.transfer_status_label.cget("text")
            self.assertIn("positive", status.lower())
    
    def test_status_display_colors(self):
        """Test ID: GUI-04"""
        self.app.show_transfer_status("Error test", "error")
        self.assertEqual(self.app.transfer_status_label.cget("fg"), '#ff0000')
        
        self.app.show_transfer_status("Success test", "success")
        self.assertEqual(self.app.transfer_status_label.cget("fg"), '#00ff00')

if __name__ == "__main__":
    unittest.main(verbosity=2)
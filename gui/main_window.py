import tkinter as tk
from tkinter import ttk, messagebox
import json
import sys

sys.path.append('models')
sys.path.append('controllers')
sys.path.append('utils')

from models.main_fuel_tank import MainFuelTank
from models.auxiliary_tank import AuxiliaryTank
from models.reserve_tank import ReserveTank
from utils.data_logger import DataLogger


class FuelManagementGUI:
   
    
    def __init__(self, root):
        self.root = root
        self.root.title("Aerospace Fuel Management System")
        self.root.geometry("1200x800")
        self.root.configure(bg='#1a1a2e')
        
        # Initialise data logger
        self.logger = DataLogger()
        self.logger.log_event("SYSTEM_START", "Fuel Management System GUI initialized")
        
        # Initialise tanks from jsons
        self.tanks = {}
        self.load_tanks_from_config()
        
        # Setup GUI
        self.setup_header()
        self.setup_main_content()
        self.setup_footer()
        
        # Automatic updates
        self.update_displays()
    
    def load_tanks_from_config(self):
        """Load tank configuration from JSON file"""
        try:
            with open('data/logs/tank_config.json', 'r') as f:
                config = json.load(f)
            
            for tank_config in config.get("tanks", []):
                tank_type = tank_config.get("type")
                tank_id = tank_config.get("tank_id")
                name = tank_config.get("name")
                capacity = tank_config.get("capacity")
                initial_fuel = tank_config.get("initial_fuel", 0)
                
                if tank_type == "MainFuelTank":
                    tank = MainFuelTank(tank_id, name, capacity, initial_fuel)
                elif tank_type == "AuxiliaryTank":
                    tank = AuxiliaryTank(tank_id, name, capacity, initial_fuel)
                elif tank_type == "ReserveTank":
                    tank = ReserveTank(tank_id, name, capacity, initial_fuel)
                else:
                    continue
                
                self.tanks[tank_id] = tank
            
            self.logger.log_event("CONFIG_LOADED", f"Loaded {len(self.tanks)} tanks from configuration")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration: {e}")
    
    def setup_header(self):
        """Setup application header"""
        header = tk.Frame(self.root, bg='#16213e', height=80)
        header.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            header,
            text="AEROSPACE FUEL MANAGEMENT SYSTEM",
            font=('Arial', 24, 'bold'),
            bg='#16213e',
            fg='#00d4ff'
        )
        title.pack(pady=20)
    
    def setup_main_content(self):
        """Setup main content area - will be filled in next commits"""
        # Main container
        self.main_frame = tk.Frame(self.root, bg='#1a1a2e')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Temporary message
        placeholder = tk.Label(
            self.main_frame,
            text="Fuel gauges and controls will be added in next commits",
            font=('Arial', 16),
            bg='#1a1a2e',
            fg='#ffffff'
        )
        placeholder.pack(pady=50)
        
        # Tank count
        tank_info = tk.Label(
            self.main_frame,
            text=f"Tanks loaded: {len(self.tanks)}",
            font=('Arial', 14),
            bg='#1a1a2e',
            fg='#00d4ff'
        )
        tank_info.pack()
    
    def setup_footer(self):
        """Setup footer with status bar"""
        footer = tk.Frame(self.root, bg='#16213e', height=40)
        footer.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(
            footer,
            text="System Status: OPERATIONAL",
            font=('Arial', 10),
            bg='#16213e',
            fg='#00ff00',
            anchor='w'
        )
        self.status_label.pack(side='left', padx=20, pady=10)
        
        # Total fuel 
        total_fuel = sum(tank.get_fuel_level() for tank in self.tanks.values())
        total_capacity = sum(tank.get_capacity() for tank in self.tanks.values())
        
        self.fuel_label = tk.Label(
            footer,
            text=f"Total Fuel: {total_fuel:.0f}L / {total_capacity:.0f}L",
            font=('Arial', 10),
            bg='#16213e',
            fg='#ffffff',
            anchor='e'
        )
        self.fuel_label.pack(side='right', padx=20, pady=10)
    
    def update_displays(self):
        """Update all display elements - called periodically"""
        # Update footer
        total_fuel = sum(tank.get_fuel_level() for tank in self.tanks.values())
        total_capacity = sum(tank.get_capacity() for tank in self.tanks.values())
        self.fuel_label.config(text=f"Total Fuel: {total_fuel:.0f}L / {total_capacity:.0f}L")
        
        # Schedule next update (every second)
        self.root.after(1000, self.update_displays)


def main():
    """Main entry point for GUI application"""
    root = tk.Tk()
    app = FuelManagementGUI(root)
    root.mainloop()

# Modularity
if __name__ == "__main__":
    main()
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
        """Setup main content area with fuel gauges"""
        # Create main container
        self.main_frame = tk.Frame(self.root, bg='#1a1a2e')
        self.main_frame.pack(fill='both', expand=True, padx=20, pady=10)
        
        # Title
        title = tk.Label(
            self.main_frame,
            text="FUEL TANK MONITORING",
            font=('Arial', 18, 'bold'),
            bg='#1a1a2e',
            fg='#00d4ff'
        )
        title.pack(pady=(0, 20))
        
        # Create gauge container
        self.gauge_frame = tk.Frame(self.main_frame, bg='#1a1a2e')
        self.gauge_frame.pack(fill='both', expand=True)
        
        # Create gauges for each tank
        self.gauge_widgets = {}
        tank_list = list(self.tanks.items())
        
        for idx, (tank_id, tank) in enumerate(tank_list):
            row = idx // 2  # 2 gauges per row
            col = idx % 2
            
            gauge = self.create_fuel_gauge(self.gauge_frame, tank_id, tank)
            gauge.grid(row=row, column=col, padx=20, pady=20, sticky='nsew')
            self.gauge_widgets[tank_id] = gauge
        
        # Configure grid weights for responsive layout
        self.gauge_frame.grid_columnconfigure(0, weight=1)
        self.gauge_frame.grid_columnconfigure(1, weight=1)
    
    def create_fuel_gauge(self, parent, tank_id, tank):
        """
        Create a fuel gauge widget for a tank.
        
        Args:
            parent: Parent widget
            tank_id: Tank identifier
            tank: Tank object
        
        Returns:
            Frame containing the gauge
        """
        # Main gauge container
        gauge_frame = tk.Frame(parent, bg='#16213e', relief='solid', borderwidth=2)
        
        # Tank name header
        name_label = tk.Label(
            gauge_frame,
            text=tank.get_name(),
            font=('Arial', 14, 'bold'),
            bg='#16213e',
            fg='#00d4ff'
        )
        name_label.pack(pady=(10, 5))
        
        # Tank ID
        id_label = tk.Label(
            gauge_frame,
            text=f"[{tank_id}]",
            font=('Arial', 10),
            bg='#16213e',
            fg='#888888'
        )
        id_label.pack()
        
        # Create canvas for visual gauge
        canvas = tk.Canvas(
            gauge_frame,
            width=200,
            height=250,
            bg='#16213e',
            highlightthickness=0
        )
        canvas.pack(pady=10)
        
        # Draw gauge background (empty tank)
        canvas.create_rectangle(
            50, 50, 150, 200,
            fill='#0f0f1e',
            outline='#00d4ff',
            width=2,
            tags=f'{tank_id}_bg'
        )
        
        # Draw fuel level (to be updated)
        percentage = tank.get_fuel_percentage()
        fuel_height = int(150 * (percentage / 100))
        fuel_y = 200 - fuel_height
        
        # Color based on status
        status = tank.get_status()
        if status == "CRITICAL":
            fuel_color = '#ff0000'
        elif status == "LOW":
            fuel_color = '#ffaa00'
        else:
            fuel_color = '#00ff00'
        
        canvas.create_rectangle(
            50, fuel_y, 150, 200,
            fill=fuel_color,
            outline='',
            tags=f'{tank_id}_fuel'
        )
        
        # Percentage markers (0%, 25%, 50%, 75%, 100%)
        for i in range(0, 101, 25):
            y = 200 - int(150 * (i / 100))
            canvas.create_line(40, y, 50, y, fill='#00d4ff', width=1)
            canvas.create_text(30, y, text=f'{i}%', fill='#00d4ff', font=('Arial', 8))
        
        # Store canvas reference in gauge_frame for updates
        gauge_frame.canvas = canvas
        gauge_frame.tank_id = tank_id
        
        # Fuel level text
        fuel_label = tk.Label(
            gauge_frame,
            text=f"{tank.get_fuel_level():.0f}L / {tank.get_capacity():.0f}L",
            font=('Arial', 12, 'bold'),
            bg='#16213e',
            fg='#ffffff'
        )
        fuel_label.pack()
        gauge_frame.fuel_label = fuel_label
        
        # Percentage text
        percentage_label = tk.Label(
            gauge_frame,
            text=f"{percentage:.1f}%",
            font=('Arial', 16, 'bold'),
            bg='#16213e',
            fg=fuel_color
        )
        percentage_label.pack()
        gauge_frame.percentage_label = percentage_label
        
        # Status indicator
        status_label = tk.Label(
            gauge_frame,
            text=f"STATUS: {status}",
            font=('Arial', 10, 'bold'),
            bg='#16213e',
            fg=fuel_color
        )
        status_label.pack(pady=(5, 0))
        gauge_frame.status_label = status_label
        
        # Pressure display
        pressure_label = tk.Label(
            gauge_frame,
            text=f"Pressure: {tank.get_pressure():.1f} PSI",
            font=('Arial', 9),
            bg='#16213e',
            fg='#cccccc'
        )
        pressure_label.pack()
        gauge_frame.pressure_label = pressure_label
        
        # Temperature display
        temp_label = tk.Label(
            gauge_frame,
            text=f"Temp: {tank.get_temperature():.1f}°C",
            font=('Arial', 9),
            bg='#16213e',
            fg='#cccccc'
        )
        temp_label.pack(pady=(0, 10))
        gauge_frame.temp_label = temp_label
        
        return gauge_frame
    
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
        # Update each gauge
        for tank_id, gauge_frame in self.gauge_widgets.items():
            tank = self.tanks[tank_id]
            
            # Get current values
            percentage = tank.get_fuel_percentage()
            status = tank.get_status()
            fuel_level = tank.get_fuel_level()
            capacity = tank.get_capacity()
            pressure = tank.get_pressure()
            temperature = tank.get_temperature()
            
            # Determine color based on status
            if status == "CRITICAL":
                fuel_color = '#ff0000'
            elif status == "LOW":
                fuel_color = '#ffaa00'
            else:
                fuel_color = '#00ff00'
            
            # Update canvas fuel level
            canvas = gauge_frame.canvas
            fuel_height = int(150 * (percentage / 100))
            fuel_y = 200 - fuel_height
            
            # Delete old fuel rectangle and create new one
            canvas.delete(f'{tank_id}_fuel')
            canvas.create_rectangle(
                50, fuel_y, 150, 200,
                fill=fuel_color,
                outline='',
                tags=f'{tank_id}_fuel'
            )
            
            # Update text labels
            gauge_frame.fuel_label.config(text=f"{fuel_level:.0f}L / {capacity:.0f}L")
            gauge_frame.percentage_label.config(text=f"{percentage:.1f}%", fg=fuel_color)
            gauge_frame.status_label.config(text=f"STATUS: {status}", fg=fuel_color)
            gauge_frame.pressure_label.config(text=f"Pressure: {pressure:.1f} PSI")
            gauge_frame.temp_label.config(text=f"Temp: {temperature:.1f}°C")
        
        # Update footer
        total_fuel = sum(tank.get_fuel_level() for tank in self.tanks.values())
        total_capacity = sum(tank.get_capacity() for tank in self.tanks.values())
        self.fuel_label.config(text=f"Total Fuel: {total_fuel:.0f}L / {total_capacity:.0f}L")
        
        # Schedule next update (every 1 second)
        self.root.after(1000, self.update_displays)


def main():
    """Main entry point for GUI application"""
    root = tk.Tk()
    app = FuelManagementGUI(root)
    root.mainloop()

# Modularity
if __name__ == "__main__":
    main()
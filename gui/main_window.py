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
        
        # Add transfer panel
        self.setup_transfer_panel()
    
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
            # Create a main container with a Canvas (scrollable)
        container = tk.Frame(self.root, bg='#1a1a2e')
        container.pack(fill='both', expand=True, padx=20, pady=10)

        # Add a canvas + scrollbar
        canvas = tk.Canvas(container, bg='#1a1a2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient='vertical', command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg='#1a1a2e')

        # Configure scrolling
        scroll_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scroll_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        # Pack everything
        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # Store reference for other setup functions
        self.main_frame = scroll_frame


        
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
      
    def setup_transfer_panel(self):
        """Setup fuel transfer control panel"""
        # Transfer panel container
        transfer_container = tk.Frame(self.main_frame, bg='#16213e', relief='solid', borderwidth=2)
        transfer_container.pack(fill='x', pady=(20, 0))
        
        # Title
        title = tk.Label(
            transfer_container,
            text="FUEL TRANSFER CONTROLS",
            font=('Arial', 14, 'bold'),
            bg='#16213e',
            fg='#00d4ff'
        )
        title.pack(pady=(10, 15))
        
        # Controls frame
        controls_frame = tk.Frame(transfer_container, bg='#16213e')
        controls_frame.pack(padx=20, pady=(0, 15))
        
        # Source tank selection
        source_label = tk.Label(
            controls_frame,
            text="Source Tank:",
            font=('Arial', 11),
            bg='#16213e',
            fg='#ffffff'
        )
        source_label.grid(row=0, column=0, padx=10, pady=5, sticky='e')
        
        self.source_var = tk.StringVar()
        tank_ids = list(self.tanks.keys())
        self.source_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.source_var,
            values=tank_ids,
            state='readonly',
            width=20,
            font=('Arial', 10)
        )
        self.source_combo.grid(row=0, column=1, padx=10, pady=5)
        if tank_ids:
            self.source_combo.current(0)
        
        # Destination tank selection
        dest_label = tk.Label(
            controls_frame,
            text="Destination Tank:",
            font=('Arial', 11),
            bg='#16213e',
            fg='#ffffff'
        )
        dest_label.grid(row=0, column=2, padx=10, pady=5, sticky='e')
        
        self.dest_var = tk.StringVar()
        self.dest_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.dest_var,
            values=tank_ids,
            state='readonly',
            width=20,
            font=('Arial', 10)
        )
        self.dest_combo.grid(row=0, column=3, padx=10, pady=5)
        if len(tank_ids) > 1:
            self.dest_combo.current(1)
        
        # Amount input
        amount_label = tk.Label(
            controls_frame,
            text="Amount (L):",
            font=('Arial', 11),
            bg='#16213e',
            fg='#ffffff'
        )
        amount_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')
        
        self.amount_var = tk.StringVar(value="500")
        amount_entry = tk.Entry(
            controls_frame,
            textvariable=self.amount_var,
            width=22,
            font=('Arial', 10)
        )
        amount_entry.grid(row=1, column=1, padx=10, pady=5)
        
                # --- Transfer button ---
        transfer_button = tk.Button(
            transfer_container,
            text="INITIATE TRANSFER",
            font=('Arial', 12, 'bold'),
            bg='#00d4ff',
            fg='black',
            activebackground='#0099cc',
            padx=10,
            pady=5,
            command=self.initiate_transfer
        )
        transfer_button.pack(pady=(5, 10))
        
        # Status message label
        self.transfer_status_label = tk.Label(
        transfer_container,
        text="",
        font=('Arial', 10),
        bg='#16213e',
        fg='#ffaa00',
        wraplength=800
        )
        self.transfer_status_label.pack(pady=(0, 10))
        
       
    def initiate_transfer(self):
        """Execute fuel transfer between tanks"""
        try:
            # Get selected tanks
            source_id = self.source_var.get()
            dest_id = self.dest_var.get()
            amount_str = self.amount_var.get()
            
            # Validation
            if not source_id or not dest_id:
                self.show_transfer_status("Error: Please select source and destination tanks", "error")
                return
            
            if source_id == dest_id:
                self.show_transfer_status("Error: Source and destination must be different", "error")
                return
            
            try:
                amount = float(amount_str)
            except ValueError:
                self.show_transfer_status("Error: Amount must be a valid number", "error")
                return
            
            if amount <= 0:
                self.show_transfer_status("Error: Amount must be positive", "error")
                return
            
            # Get tanks
            source_tank = self.tanks.get(source_id)
            dest_tank = self.tanks.get(dest_id)
            
            if not source_tank or not dest_tank:
                self.show_transfer_status("Error: Invalid tank selection", "error")
                return
            
            # Check if source is reserve tank
            if hasattr(source_tank, 'is_emergency_mode'):
                if not source_tank.is_emergency_mode():
                    response = messagebox.askyesno(
                        "Reserve Tank Warning",
                        f"{source_tank.get_name()} is a reserve tank.\n\n"
                        "Emergency mode must be activated to transfer fuel.\n\n"
                        "Activate emergency mode?"
                    )
                    if response:
                        source_tank.activate_emergency_mode()
                        self.logger.log_event("EMERGENCY_MODE", f"Emergency mode activated for {source_id}")
                    else:
                        self.show_transfer_status("Transfer cancelled - Emergency mode not activated", "warning")
                        return
            
            # Validate source has enough fuel
            if source_tank.get_fuel_level() < amount:
                self.show_transfer_status(
                    f"Error: Insufficient fuel in {source_id} "
                    f"(Available: {source_tank.get_fuel_level():.1f}L)",
                    "error"
                )
                return
            
            # Validate destination has capacity
            if dest_tank.get_available_capacity() < amount:
                self.show_transfer_status(
                    f"Error: Insufficient capacity in {dest_id} "
                    f"(Available: {dest_tank.get_available_capacity():.1f}L)",
                    "error"
                )
                return
            
            # Execute transfer
            remove_success = source_tank.remove_fuel(amount)
            if not remove_success:
                self.show_transfer_status("Error: Failed to remove fuel from source tank", "error")
                self.logger.log_transfer(source_id, dest_id, amount, False)
                return
            
            add_success = dest_tank.add_fuel(amount)
            if not add_success:
                # Rollback
                source_tank.add_fuel(amount)
                self.show_transfer_status("Error: Failed to add fuel to destination tank", "error")
                self.logger.log_transfer(source_id, dest_id, amount, False)
                return
            
            # Success!
            self.show_transfer_status(
                f"✓ Successfully transferred {amount:.1f}L from {source_id} to {dest_id}",
                "success"
            )
            self.logger.log_transfer(source_id, dest_id, amount, True)
            
            # Update displays immediately
            self.update_displays()
            
        except Exception as e:
            self.show_transfer_status(f"Error: {str(e)}", "error")
            self.logger.log_event("TRANSFER_ERROR", str(e), severity="WARNING")

    def show_transfer_status(self, message, status_type):
        """
        Show transfer status message.
        
        Args:
            message: Status message
            status_type: 'success', 'error', or 'warning'
        """
        colors = {
            'success': '#00ff00',
            'error': '#ff0000',
            'warning': '#ffaa00'
        }
        self.transfer_status_label.config(
            text=message,
            fg=colors.get(status_type, '#ffffff')
        )
            
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
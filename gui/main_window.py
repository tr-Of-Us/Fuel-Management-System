import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import sys
sys.path.append('models')
sys.path.append('controllers')
sys.path.append('utils')

#Fixed issue of not running with debugger
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.main_fuel_tank import MainFuelTank
from models.auxiliary_tank import AuxiliaryTank
from models.reserve_tank import ReserveTank
from utils.data_logger import DataLogger


class FuelManagementGUI:
    """Main GUI application for Fuel Management System"""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Aerospace Fuel Management System")
        self.root.geometry("1400x900")  # Made wider and taller
        self.root.configure(bg='#1a1a2e')
        
        # Initialize data logger
        self.logger = DataLogger()
        self.logger.log_event("SYSTEM_START", "Fuel Management System GUI initialized")
        
        # Initialize tanks
        self.tanks = {}
        self.load_tanks_from_config()
        
        # Setup GUI
        self.setup_header()
        self.setup_main_layout()
        self.setup_footer()
        
        # Start automatic updates
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
        header = tk.Frame(self.root, bg='#16213e', height=70)
        header.pack(fill='x', pady=(0, 10))
        
        title = tk.Label(
            header,
            text="AEROSPACE FUEL MANAGEMENT SYSTEM",
            font=('Arial', 22, 'bold'),
            bg='#16213e',
            fg='#00d4ff'
        )
        title.pack(pady=15)
    
    def setup_main_layout(self):
        """Setup main layout with left panel (gauges/transfer) and right panel (logs)"""
        # Main container - split into left and right
        self.main_container = tk.Frame(self.root, bg='#1a1a2e')
        self.main_container.pack(fill='both', expand=True, padx=20, pady=10)
        
        # LEFT PANEL - Gauges and Transfer
        left_panel = tk.Frame(self.main_container, bg='#1a1a2e')
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))
        
        # Gauges title
        gauges_title = tk.Label(
            left_panel,
            text="FUEL TANK MONITORING",
            font=('Arial', 16, 'bold'),
            bg='#1a1a2e',
            fg='#00d4ff'
        )
        gauges_title.pack(pady=(0, 15))
        
        # Create canvas with scrollbar for gauges
        canvas_frame = tk.Frame(left_panel, bg='#1a1a2e')
        canvas_frame.pack(fill='both', expand=True)
        
        # Canvas and scrollbar
        self.gauge_canvas = tk.Canvas(canvas_frame, bg='#1a1a2e', highlightthickness=0)
        scrollbar = tk.Scrollbar(canvas_frame, orient='vertical', command=self.gauge_canvas.yview)
        
        self.scrollable_gauge_frame = tk.Frame(self.gauge_canvas, bg='#1a1a2e')
        
        self.scrollable_gauge_frame.bind(
            "<Configure>",
            lambda e: self.gauge_canvas.configure(scrollregion=self.gauge_canvas.bbox("all"))
        )
        
        self.gauge_canvas.create_window((0, 0), window=self.scrollable_gauge_frame, anchor="nw")
        self.gauge_canvas.configure(yscrollcommand=scrollbar.set)
        
        self.gauge_canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Create gauges (2x2 grid)
        self.gauge_widgets = {}
        tank_list = list(self.tanks.items())
        
        for idx, (tank_id, tank) in enumerate(tank_list):
            row = idx // 2
            col = idx % 2
            
            gauge = self.create_fuel_gauge(self.scrollable_gauge_frame, tank_id, tank)
            gauge.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')
            self.gauge_widgets[tank_id] = gauge
        
        # Configure grid weights
        self.scrollable_gauge_frame.grid_columnconfigure(0, weight=1)
        self.scrollable_gauge_frame.grid_columnconfigure(1, weight=1)
        
        # Transfer panel (below gauges in left panel)
        self.setup_transfer_panel(left_panel)
        
        # RIGHT PANEL - Logs
        self.setup_log_panel(self.main_container)
    
    def create_fuel_gauge(self, parent, tank_id, tank):
        """Create a fuel gauge widget for a tank"""
        # Main gauge container - made more compact
        gauge_frame = tk.Frame(parent, bg='#16213e', relief='solid', borderwidth=2)
        
        # Tank name header
        name_label = tk.Label(
            gauge_frame,
            text=tank.get_name(),
            font=('Arial', 12, 'bold'),
            bg='#16213e',
            fg='#00d4ff'
        )
        name_label.pack(pady=(8, 3))
        
        # Tank ID
        id_label = tk.Label(
            gauge_frame,
            text=f"[{tank_id}]",
            font=('Arial', 9),
            bg='#16213e',
            fg='#888888'
        )
        id_label.pack()
        
        # Create canvas for visual gauge - smaller
        canvas = tk.Canvas(
            gauge_frame,
            width=160,
            height=200,
            bg='#16213e',
            highlightthickness=0
        )
        canvas.pack(pady=8)
        
        # Draw gauge background
        canvas.create_rectangle(
            40, 40, 120, 160,
            fill='#0f0f1e',
            outline='#00d4ff',
            width=2,
            tags=f'{tank_id}_bg'
        )
        
        # Draw fuel level
        percentage = tank.get_fuel_percentage()
        fuel_height = int(120 * (percentage / 100))
        fuel_y = 160 - fuel_height
        
        status = tank.get_status()
        if status == "CRITICAL":
            fuel_color = '#ff0000'
        elif status == "LOW":
            fuel_color = '#ffaa00'
        else:
            fuel_color = '#00ff00'
        
        canvas.create_rectangle(
            40, fuel_y, 120, 160,
            fill=fuel_color,
            outline='',
            tags=f'{tank_id}_fuel'
        )
        
        # Percentage markers
        for i in range(0, 101, 25):
            y = 160 - int(120 * (i / 100))
            canvas.create_line(30, y, 40, y, fill='#00d4ff', width=1)
            canvas.create_text(20, y, text=f'{i}%', fill='#00d4ff', font=('Arial', 7))
        
        gauge_frame.canvas = canvas
        gauge_frame.tank_id = tank_id
        
        # Fuel level text - compact
        fuel_label = tk.Label(
            gauge_frame,
            text=f"{tank.get_fuel_level():.0f}L / {tank.get_capacity():.0f}L",
            font=('Arial', 10, 'bold'),
            bg='#16213e',
            fg='#ffffff'
        )
        fuel_label.pack()
        gauge_frame.fuel_label = fuel_label
        
        # Percentage text
        percentage_label = tk.Label(
            gauge_frame,
            text=f"{percentage:.1f}%",
            font=('Arial', 14, 'bold'),
            bg='#16213e',
            fg=fuel_color
        )
        percentage_label.pack()
        gauge_frame.percentage_label = percentage_label
        
        # Status indicator
        status_label = tk.Label(
            gauge_frame,
            text=f"STATUS: {status}",
            font=('Arial', 9, 'bold'),
            bg='#16213e',
            fg=fuel_color
        )
        status_label.pack(pady=(3, 0))
        gauge_frame.status_label = status_label
        
        # Pressure display
        pressure_label = tk.Label(
            gauge_frame,
            text=f"Pressure: {tank.get_pressure():.1f} PSI",
            font=('Arial', 8),
            bg='#16213e',
            fg='#cccccc'
        )
        pressure_label.pack()
        gauge_frame.pressure_label = pressure_label
        
        # Temperature display
        temp_label = tk.Label(
            gauge_frame,
            text=f"Temp: {tank.get_temperature():.1f}°C",
            font=('Arial', 8),
            bg='#16213e',
            fg='#cccccc'
        )
        temp_label.pack(pady=(0, 8))
        gauge_frame.temp_label = temp_label
        
        return gauge_frame
    
    def setup_transfer_panel(self, parent):
        """Setup fuel transfer control panel"""
        transfer_container = tk.Frame(parent, bg='#16213e', relief='solid', borderwidth=2)
        transfer_container.pack(fill='x', pady=(15, 0))
        
        # Title
        title = tk.Label(
            transfer_container,
            text="FUEL TRANSFER CONTROLS",
            font=('Arial', 12, 'bold'),
            bg='#16213e',
            fg='#00d4ff'
        )
        title.pack(pady=(8, 10))
        
        # Controls frame
        controls_frame = tk.Frame(transfer_container, bg='#16213e')
        controls_frame.pack(padx=15, pady=(0, 10))
        
        # Source tank
        source_label = tk.Label(
            controls_frame,
            text="Source:",
            font=('Arial', 10),
            bg='#16213e',
            fg='#ffffff'
        )
        source_label.grid(row=0, column=0, padx=8, pady=4, sticky='e')
        
        self.source_var = tk.StringVar()
        tank_ids = list(self.tanks.keys())
        self.source_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.source_var,
            values=tank_ids,
            state='readonly',
            width=18,
            font=('Arial', 9)
        )
        self.source_combo.grid(row=0, column=1, padx=8, pady=4)
        if tank_ids:
            self.source_combo.current(0)
        
        # Destination tank
        dest_label = tk.Label(
            controls_frame,
            text="Destination:",
            font=('Arial', 10),
            bg='#16213e',
            fg='#ffffff'
        )
        dest_label.grid(row=0, column=2, padx=8, pady=4, sticky='e')
        
        self.dest_var = tk.StringVar()
        self.dest_combo = ttk.Combobox(
            controls_frame,
            textvariable=self.dest_var,
            values=tank_ids,
            state='readonly',
            width=18,
            font=('Arial', 9)
        )
        self.dest_combo.grid(row=0, column=3, padx=8, pady=4)
        if len(tank_ids) > 1:
            self.dest_combo.current(1)
        
        # Amount
        amount_label = tk.Label(
            controls_frame,
            text="Amount (L):",
            font=('Arial', 10),
            bg='#16213e',
            fg='#ffffff'
        )
        amount_label.grid(row=1, column=0, padx=8, pady=4, sticky='e')
        
        self.amount_var = tk.StringVar(value="500")
        amount_entry = tk.Entry(
            controls_frame,
            textvariable=self.amount_var,
            width=20,
            font=('Arial', 9)
        )
        amount_entry.grid(row=1, column=1, padx=8, pady=4)
        
        # Quick buttons
        quick_frame = tk.Frame(controls_frame, bg='#16213e')
        quick_frame.grid(row=1, column=2, columnspan=2, padx=8, pady=4)
        
        quick_label = tk.Label(
            quick_frame,
            text="Quick:",
            font=('Arial', 8),
            bg='#16213e',
            fg='#888888'
        )
        quick_label.pack(side='left', padx=(0, 5))
        
        for amount in [100, 500, 1000]:
            btn = tk.Button(
                quick_frame,
                text=f"{amount}L",
                command=lambda a=amount: self.amount_var.set(str(a)),
                bg='#0f3460',
                fg='#ffffff',
                font=('Arial', 8),
                relief='raised',
                borderwidth=1,
                padx=8,
                pady=2
            )
            btn.pack(side='left', padx=2)
        
        # Transfer button
        transfer_btn = tk.Button(
            controls_frame,
            text="INITIATE TRANSFER",
            command=self.initiate_transfer,
            bg='#00d4ff',
            fg='#000000',
            font=('Arial', 11, 'bold'),
            relief='raised',
            borderwidth=2,
            padx=15,
            pady=8,
            cursor='hand2'
        )
        transfer_btn.grid(row=2, column=0, columnspan=4, pady=(10, 8))
        
        # Status message
        self.transfer_status_label = tk.Label(
            transfer_container,
            text="",
            font=('Arial', 9),
            bg='#16213e',
            fg='#ffaa00',
            wraplength=600
        )
        self.transfer_status_label.pack(pady=(0, 8))
    
    def setup_log_panel(self, parent):
        """Setup system log display panel"""
        # Log panel container
        log_container = tk.Frame(parent, bg='#16213e', relief='solid', borderwidth=2, width=400)
        log_container.pack(side='right', fill='both', expand=False)
        log_container.pack_propagate(False)
        
        # Title
        log_title = tk.Label(
            log_container,
            text="SYSTEM LOGS",
            font=('Arial', 14, 'bold'),
            bg='#16213e',
            fg='#00d4ff'
        )
        log_title.pack(pady=(10, 10))
        
        # Log text area with scrollbar
        self.log_text = scrolledtext.ScrolledText(
            log_container,
            width=45,
            height=35,
            bg='#0f0f1e',
            fg='#00ff00',
            font=('Courier', 9),
            wrap='word',
            state='disabled'
        )
        self.log_text.pack(padx=10, pady=(0, 10), fill='both', expand=True)
        
        # Configure text tags for colors
        self.log_text.tag_config('INFO', foreground='#00ff00')
        self.log_text.tag_config('WARNING', foreground='#ffaa00')
        self.log_text.tag_config('CRITICAL', foreground='#ff0000')
        self.log_text.tag_config('SYSTEM', foreground='#00d4ff')
        
        # Button frame
        btn_frame = tk.Frame(log_container, bg='#16213e')
        btn_frame.pack(pady=(0, 10))
        
        # Clear logs button
        clear_btn = tk.Button(
            btn_frame,
            text="Clear Logs",
            command=self.clear_logs,
            bg='#0f3460',
            fg='#ffffff',
            font=('Arial', 9),
            padx=10,
            pady=5
        )
        clear_btn.pack(side='left', padx=5)
        
        
        # Display initial logs
        self.refresh_logs()
    
    def add_log_entry(self, message, severity='INFO'):
        """
        Add a log entry to the log display.
        
        Args:
            message: Log message
            severity: Log severity (INFO, WARNING, CRITICAL, SYSTEM)
        """
        self.log_text.config(state='normal')
        
        from datetime import datetime
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_line = f"[{timestamp}] {message}\n"
        
        self.log_text.insert('end', log_line, severity)
        self.log_text.see('end')  # Auto-scroll to bottom
        
        self.log_text.config(state='disabled')
    
    def refresh_logs(self):
        """Refresh log display with all logger entries"""
        self.log_text.config(state='normal')
        self.log_text.delete('1.0', 'end')
        
        for log in self.logger.get_logs():
            timestamp = log.get('timestamp', '')
            if timestamp:
                # Extract time only
                time_part = timestamp.split('T')[1].split('.')[0] if 'T' in timestamp else timestamp
            else:
                time_part = "00:00:00"
            
            message = log.get('message', '')
            severity = log.get('severity', 'INFO')
            
            log_line = f"[{time_part}] {message}\n"
            self.log_text.insert('end', log_line, severity)
    
    def clear_logs(self):
        """Clear all logs"""
        response = messagebox.askyesno("Clear Logs", "Are you sure you want to clear all logs?")
        if response:
            self.logger.clear_logs()
            self.log_text.config(state='normal')
            self.log_text.delete('1.0', 'end')
            self.log_text.config(state='disabled')
            self.add_log_entry("Logs cleared", "SYSTEM")
    

    def initiate_transfer(self):
        """Execute fuel transfer between tanks"""
        try:
            source_id = self.source_var.get()
            dest_id = self.dest_var.get()
            amount_str = self.amount_var.get()
            
            # Validation
            if not source_id or not dest_id:
                self.show_transfer_status("Error: Select source and destination", "error")
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
            
            source_tank = self.tanks.get(source_id)
            dest_tank = self.tanks.get(dest_id)
            
            if not source_tank or not dest_tank:
                self.show_transfer_status("Error: Invalid tank selection", "error")
                return
            
            # Check reserve tank
            if hasattr(source_tank, 'is_emergency_mode'):
                if not source_tank.is_emergency_mode():
                    response = messagebox.askyesno(
                        "Reserve Tank Warning",
                        f"{source_tank.get_name()} is a reserve tank.\n\n"
                        "Emergency mode must be activated.\n\n"
                        "Activate emergency mode?"
                    )
                    if response:
                        source_tank.activate_emergency_mode()
                        self.logger.log_event("EMERGENCY_MODE", f"Emergency mode activated for {source_id}")
                        self.add_log_entry(f"Emergency mode activated: {source_id}", "WARNING")
                    else:
                        self.show_transfer_status("Transfer cancelled", "warning")
                        return
            
            # Validate
            if source_tank.get_fuel_level() < amount:
                self.show_transfer_status(
                    f"Error: Insufficient fuel in {source_id} (Available: {source_tank.get_fuel_level():.1f}L)",
                    "error"
                )
                return
            
            if dest_tank.get_available_capacity() < amount:
                self.show_transfer_status(
                    f"Error: Insufficient capacity in {dest_id} (Available: {dest_tank.get_available_capacity():.1f}L)",
                    "error"
                )
                return
            
            # Execute transfer
            remove_success = source_tank.remove_fuel(amount)
            if not remove_success:
                self.show_transfer_status("Error: Failed to remove fuel", "error")
                self.logger.log_transfer(source_id, dest_id, amount, False)
                self.add_log_entry(f"Transfer FAILED: {source_id} → {dest_id} ({amount}L)", "WARNING")
                return
            
            add_success = dest_tank.add_fuel(amount)
            if not add_success:
                source_tank.add_fuel(amount)  # Rollback
                self.show_transfer_status("Error: Failed to add fuel (rolled back)", "error")
                self.logger.log_transfer(source_id, dest_id, amount, False)
                self.add_log_entry(f"Transfer FAILED: {source_id} → {dest_id} ({amount}L)", "WARNING")
                return
            
            # Success
            self.show_transfer_status(
                f"✓ Transferred {amount:.1f}L from {source_id} to {dest_id}",
                "success"
            )
            self.logger.log_transfer(source_id, dest_id, amount, True)
            self.add_log_entry(f"Transfer SUCCESS: {source_id} → {dest_id} ({amount:.1f}L)", "INFO")
            
            self.update_displays()
            
        except Exception as e:
            self.show_transfer_status(f"Error: {str(e)}", "error")
            self.logger.log_event("TRANSFER_ERROR", str(e), severity="WARNING")
            self.add_log_entry(f"Transfer ERROR: {str(e)}", "CRITICAL")
    
    def show_transfer_status(self, message, status_type):
        """Show transfer status message"""
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
        footer = tk.Frame(self.root, bg='#16213e', height=35)
        footer.pack(fill='x', side='bottom')
        
        self.status_label = tk.Label(
            footer,
            text="System Status: OPERATIONAL",
            font=('Arial', 9),
            bg='#16213e',
            fg='#00ff00',
            anchor='w'
        )
        self.status_label.pack(side='left', padx=20, pady=8)
        
        total_fuel = sum(tank.get_fuel_level() for tank in self.tanks.values())
        total_capacity = sum(tank.get_capacity() for tank in self.tanks.values())
        
        self.fuel_label = tk.Label(
            footer,
            text=f"Total Fuel: {total_fuel:.0f}L / {total_capacity:.0f}L",
            font=('Arial', 9),
            bg='#16213e',
            fg='#ffffff',
            anchor='e'
        )
        self.fuel_label.pack(side='right', padx=20, pady=8)
    
    def update_displays(self):
        """Update all display elements"""
        # Update gauges
        for tank_id, gauge_frame in self.gauge_widgets.items():
            tank = self.tanks[tank_id]
            
            percentage = tank.get_fuel_percentage()
            status = tank.get_status()
            
            if status == "CRITICAL":
                fuel_color = '#ff0000'
            elif status == "LOW":
                fuel_color = '#ffaa00'
            else:
                fuel_color = '#00ff00'
            
            canvas = gauge_frame.canvas
            fuel_height = int(120 * (percentage / 100))
            fuel_y = 160 - fuel_height
            
            canvas.delete(f'{tank_id}_fuel')
            canvas.create_rectangle(
                40, fuel_y, 120, 160,
                fill=fuel_color,
                outline='',
                tags=f'{tank_id}_fuel'
            )
            
            gauge_frame.fuel_label.config(text=f"{tank.get_fuel_level():.0f}L / {tank.get_capacity():.0f}L")
            gauge_frame.percentage_label.config(text=f"{percentage:.1f}%", fg=fuel_color)
            gauge_frame.status_label.config(text=f"STATUS: {status}", fg=fuel_color)
            gauge_frame.pressure_label.config(text=f"Pressure: {tank.get_pressure():.1f} PSI")
            gauge_frame.temp_label.config(text=f"Temp: {tank.get_temperature():.1f}°C")
        
        # Update footer
        total_fuel = sum(tank.get_fuel_level() for tank in self.tanks.values())
        total_capacity = sum(tank.get_capacity() for tank in self.tanks.values())
        self.fuel_label.config(text=f"Total Fuel: {total_fuel:.0f}L / {total_capacity:.0f}L")
        
        self.root.after(1000, self.update_displays)


def main():
    """Main entry point"""
    root = tk.Tk()
    app = FuelManagementGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
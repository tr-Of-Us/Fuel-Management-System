import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import json
import sys

sys.path.append('models')
sys.path.append('controllers')
sys.path.append('utils')

from models.main_fuel_tank import MainFuelTank
from models.auxiliary_tank import AuxiliaryTank
from models.reserve_tank import ReserveTank
from utils.data_logger import DataLogger
from controllers.fuel_transfer_controller import FuelTransferController
from controllers.fuel_system import FuelSystem


class FuelManagementGUI:
    """Simplified GUI for Aerospace Fuel Management System"""

    def __init__(self, root):
        self.root = root
        self.root.title("Aerospace Fuel Management System")
        self.root.geometry("1300x850")
        self.root.configure(bg='#0a0e27')

        # Logger and Fuel System
        self.logger = DataLogger()
        self.fuel_system = FuelSystem()
        self.load_tanks_from_config()
        self.transfer_controller = FuelTransferController(self.fuel_system, self.logger)

        self.setup_styles()
        self.setup_header()
        self.setup_main_layout()
        self.setup_footer()

        self.logger.log_event("SYSTEM_START", "Fuel Management GUI initialized")
        self.update_displays()

    # --------------------------- Setup & Config ----------------------------

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TCombobox',
                        fieldbackground='#1a1a2e',
                        background='#16213e',
                        foreground='#ffffff',
                        arrowcolor='#00d4ff')

    def load_tanks_from_config(self):
        """Load tank data from config file"""
        try:
            with open('data/logs/tank_config.json', 'r') as f:
                config = json.load(f)

            for t in config.get("tanks", []):
                tank_type = t.get("type")
                tank_id, name = t.get("tank_id"), t.get("name")
                capacity, initial = t.get("capacity"), t.get("initial_fuel", 0)

                if tank_type == "MainFuelTank":
                    tank = MainFuelTank(tank_id, name, capacity, initial)
                elif tank_type == "AuxiliaryTank":
                    tank = AuxiliaryTank(tank_id, name, capacity, initial)
                elif tank_type == "ReserveTank":
                    tank = ReserveTank(tank_id, name, capacity, initial)
                else:
                    continue

                self.fuel_system.add_tank(tank)

            self.logger.log_event("CONFIG_LOADED", f"Loaded {len(self.fuel_system.get_tank_ids())} tanks")

        except Exception as e:
            messagebox.showerror("Config Error", f"Failed to load configuration:\n{e}")

    # --------------------------- Header ----------------------------

    def setup_header(self):
        header = tk.Frame(self.root, bg='#16213e', height=80)
        header.pack(fill='x')

        title = tk.Label(header, text="AEROSPACE FUEL MANAGEMENT SYSTEM",
                         font=('Arial', 22, 'bold'), bg='#16213e', fg='#00d4ff')
        title.pack(pady=20)

        tk.Frame(self.root, bg='#00d4ff', height=2).pack(fill='x')

    # --------------------------- Main Layout ----------------------------

    def setup_main_layout(self):
        main = tk.Frame(self.root, bg='#0a0e27')
        main.pack(fill='both', expand=True, padx=15, pady=15)

        left = tk.Frame(main, bg='#0a0e27')
        left.pack(side='left', fill='both', expand=True, padx=(0, 10))
        right = tk.Frame(main, bg='#16213e', width=420)
        right.pack(side='right', fill='both')

        # Left: Gauges + Transfer
        self.create_gauges(left)
        self.create_transfer_panel(left)

        # Right: Logs
        self.create_log_panel(right)

    # --------------------------- Gauges ----------------------------

    def create_gauges(self, parent):
        label = tk.Label(parent, text="FUEL TANK MONITORING", font=('Arial', 16, 'bold'),
                         bg='#0a0e27', fg='#00d4ff')
        label.pack(pady=(0, 10))

        frame = tk.Frame(parent, bg='#0a0e27')
        frame.pack(fill='both', expand=True)

        canvas = tk.Canvas(frame, bg='#0a0e27', highlightthickness=0)
        scrollbar = tk.Scrollbar(frame, orient='vertical', command=canvas.yview)
        self.gauge_frame = tk.Frame(canvas, bg='#0a0e27')

        self.gauge_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.gauge_frame, anchor='nw')
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        self.gauge_widgets = {}
        for idx, tank in enumerate(self.fuel_system.get_all_tanks().values()):
            gf = self.create_gauge(self.gauge_frame, tank.get_tank_id(), tank)
            gf.grid(row=idx // 2, column=idx % 2, padx=10, pady=10, sticky='nsew')
            self.gauge_widgets[tank.get_tank_id()] = gf

        self.gauge_frame.grid_columnconfigure(0, weight=1)
        self.gauge_frame.grid_columnconfigure(1, weight=1)

    def create_gauge(self, parent, tank_id, tank):
        frame = tk.Frame(parent, bg='#16213e', relief='ridge', borderwidth=2)
        tk.Label(frame, text=f"{tank.get_name()} ({tank_id})",
                 font=('Arial', 11, 'bold'), bg='#16213e', fg='#00d4ff').pack(pady=6)

        c = tk.Canvas(frame, width=160, height=180, bg='#16213e', highlightthickness=0)
        c.pack(pady=5)
        c.create_rectangle(50, 40, 110, 160, fill='#0a0e27', outline='#00d4ff', width=2, tags=f"{tank_id}_bg")

        fuel_height = int(120 * (tank.get_fuel_percentage() / 100))
        c.create_rectangle(50, 160 - fuel_height, 110, 160,
                           fill=self.status_color(tank.get_status()), outline='', tags=f"{tank_id}_fuel")

        lbl = tk.Label(frame, text=f"{tank.get_fuel_level():.0f}L / {tank.get_capacity():.0f}L",
                       font=('Arial', 10, 'bold'), bg='#16213e', fg='#ffffff')
        lbl.pack(pady=(2, 0))
        perc = tk.Label(frame, text=f"{tank.get_fuel_percentage():.1f}%",
                        font=('Arial', 14, 'bold'), bg='#16213e', fg=self.status_color(tank.get_status()))
        perc.pack(pady=2)

        frame.fuel_label = lbl
        frame.percentage_label = perc
        frame.canvas = c
        frame.tank_id = tank_id
        return frame

    def status_color(self, status):
        return {'NORMAL': '#00ff00', 'LOW': '#ffaa00', 'CRITICAL': '#ff0000'}.get(status, '#00ff00')

    # --------------------------- Transfer Panel ----------------------------

    def create_transfer_panel(self, parent):
        panel = tk.Frame(parent, bg='#16213e', relief='ridge', borderwidth=2)
        panel.pack(fill='x', pady=15)

        tk.Label(panel, text="FUEL TRANSFER CONTROLS",
                 font=('Arial', 13, 'bold'), bg='#1a2332', fg='#00d4ff').pack(fill='x', pady=8)

        frame = tk.Frame(panel, bg='#16213e')
        frame.pack(pady=8)

        tk.Label(frame, text="Source:", bg='#16213e', fg='#00d4ff').grid(row=0, column=0, sticky='e', padx=5)
        self.source_var = tk.StringVar()
        self.source_combo = ttk.Combobox(frame, textvariable=self.source_var,
                                         values=self.fuel_system.get_tank_ids(), state='readonly', width=18)
        self.source_combo.grid(row=0, column=1, padx=5)

        tk.Label(frame, text="→", bg='#16213e', fg='#00d4ff').grid(row=0, column=2, padx=5)

        tk.Label(frame, text="Destination:", bg='#16213e', fg='#00d4ff').grid(row=0, column=3, sticky='e', padx=5)
        self.dest_var = tk.StringVar()
        self.dest_combo = ttk.Combobox(frame, textvariable=self.dest_var,
                                       values=self.fuel_system.get_tank_ids(), state='readonly', width=18)
        self.dest_combo.grid(row=0, column=4, padx=5)

        tk.Label(frame, text="Amount (L):", bg='#16213e', fg='#00d4ff').grid(row=1, column=0, sticky='e', padx=5)
        self.amount_var = tk.StringVar(value="500")
        tk.Entry(frame, textvariable=self.amount_var, width=20, bg='#1a1a2e', fg='#ffffff').grid(row=1, column=1, padx=5)

        tk.Button(frame, text="INITIATE TRANSFER", command=self.initiate_transfer,
                  bg='#00d4ff', fg='#000', font=('Arial', 10, 'bold'), relief='raised').grid(
            row=2, column=0, columnspan=5, pady=10)

        self.transfer_status_label = tk.Label(panel, text="Ready for transfer",
                                              bg='#0f1419', fg='#888888', pady=5)
        self.transfer_status_label.pack(fill='x', pady=5)

    # --------------------------- Logs Panel ----------------------------

    def create_log_panel(self, parent):
        tk.Label(parent, text="SYSTEM LOGS", font=('Arial', 14, 'bold'),
                 bg='#1a2332', fg='#00d4ff').pack(fill='x', pady=8)

        frame = tk.Frame(parent, bg='#0a0e27', relief='sunken', borderwidth=2)
        frame.pack(fill='both', expand=True, padx=10, pady=10)

        self.log_text = scrolledtext.ScrolledText(frame, bg='#0a0e27', fg='#00ff00',
                                                  font=('Courier', 9), state='disabled')
        self.log_text.pack(fill='both', expand=True)

        btns = tk.Frame(parent, bg='#16213e')
        btns.pack(pady=5)
        tk.Button(btns, text="Clear", command=self.clear_logs,
                  bg='#ff4444', fg='#fff').pack(side='left', padx=5)
        tk.Button(btns, text="Export", command=self.export_logs,
                  bg='#0f3460', fg='#fff').pack(side='left', padx=5)

    def add_log_entry(self, msg, severity='INFO'):
        self.log_text.config(state='normal')
        from datetime import datetime
        t = datetime.now().strftime('%H:%M:%S')
        self.log_text.insert('end', f"[{t}] {msg}\n")
        self.log_text.see('end')
        self.log_text.config(state='disabled')

    def clear_logs(self):
        if messagebox.askyesno("Clear Logs", "Are you sure you want to clear logs?"):
            self.logger.clear_logs()
            self.log_text.config(state='normal')
            self.log_text.delete('1.0', 'end')
            self.log_text.config(state='disabled')
            self.add_log_entry("Logs cleared", "SYSTEM")

    def export_logs(self):
        if self.logger.save_to_file():
            messagebox.showinfo("Export", "Logs exported to data/logs/system_log.json")

    # --------------------------- Transfer Logic ----------------------------

    def initiate_transfer(self):
        try:
            src, dest, amt_str = self.source_var.get(), self.dest_var.get(), self.amount_var.get()
            if not src or not dest:
                return self.show_transfer_status("Error: Select both tanks", "error")
            try:
                amt = float(amt_str)
            except ValueError:
                return self.show_transfer_status("Error: Invalid amount", "error")
            if amt <= 0:
                return self.show_transfer_status("Error: Amount must be positive", "error")

            # Handle reserve tank emergency prompt if source is ReserveTank
            source_tank = self.fuel_system.get_tank(src)
            if hasattr(source_tank, 'is_emergency_mode') and not source_tank.is_emergency_mode():
                if messagebox.askyesno("Reserve Tank", f"Activate emergency mode for {source_tank.get_name()}?"):
                    source_tank.activate_emergency_mode()
                else:
                    return self.show_transfer_status("Transfer cancelled", "warning")

            # Execute transfer via controller
            success, msg = self.transfer_controller.execute_transfer(src, dest, amt)
            self.show_transfer_status(msg, "success" if success else "error")
            if success:
                self.add_log_entry(f"Transfer {amt:.1f}L from {src} → {dest}", "INFO")

            self.update_displays()

        except Exception as e:
            self.show_transfer_status(f"Error: {e}", "error")

    def show_transfer_status(self, msg, stype):
        color = {'success': '#00ff00', 'error': '#ff0000', 'warning': '#ffaa00'}.get(stype, '#ffffff')
        self.transfer_status_label.config(text=msg, fg=color)

    # --------------------------- Footer & Updates ----------------------------

    def setup_footer(self):
        tk.Frame(self.root, bg='#00d4ff', height=2).pack(fill='x', side='bottom')
        footer = tk.Frame(self.root, bg='#16213e', height=40)
        footer.pack(fill='x', side='bottom')

        self.status_label = tk.Label(footer, text="System: OPERATIONAL",
                                     bg='#16213e', fg='#00ff00', font=('Arial', 10, 'bold'))
        self.status_label.pack(side='left', padx=20)

        self.total_label = tk.Label(footer, text="", bg='#16213e', fg='#ffffff', font=('Arial', 10))
        self.total_label.pack(side='right', padx=20)

    def update_displays(self):
        for tid, gf in self.gauge_widgets.items():
            t = self.fuel_system.get_tank(tid)
            perc = t.get_fuel_percentage()
            color = self.status_color(t.get_status())

            gf.canvas.delete(f"{tid}_fuel")
            fuel_h = int(120 * (perc / 100))
            gf.canvas.create_rectangle(50, 160 - fuel_h, 110, 160, fill=color, outline='', tags=f"{tid}_fuel")

            gf.fuel_label.config(text=f"{t.get_fuel_level():.0f}L / {t.get_capacity():.0f}L")
            gf.percentage_label.config(text=f"{perc:.1f}%", fg=color)

        total = self.fuel_system.get_total_fuel()
        cap = self.fuel_system.get_total_capacity()
        self.total_label.config(text=f"Total: {total:.0f}L / {cap:.0f}L")
        self.root.after(1000, self.update_displays)


def main():
    root = tk.Tk()
    app = FuelManagementGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

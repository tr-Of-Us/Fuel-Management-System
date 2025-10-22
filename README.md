# Fuel-Management-System
# Aerospace Fuel Management System

## Project Overview
A modular object-oriented fuel management system for aerospace simulation, developed as part of the DN5MD003 Object-Oriented Programming assessment for AeroSim Dynamics.

## System Description
This fuel management system simulates a real-world aerospace fuel control system with the following capabilities:

## Project Structure
```
fuel-management-system/
├── main.py                    # Application entry point
├── models/                    # Core OOP classes (tanks, sensors)
├── controllers/               # Business logic (fuel system, transfers)
├── utils/                     # Utilities (logging, alerts, data transfer)
├── gui/                       # GUI components (dashboard, panels, widgets)
├── data/                      # JSON configuration and state files
├── tests/                     # Unit and integration tests
└── examples/                  # Demo configurations
```
## Installation

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Git

### Setup Instructions
1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/fuel-management-system.git
   cd fuel-management-system
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:
   ```bash
   python main.py
   ```
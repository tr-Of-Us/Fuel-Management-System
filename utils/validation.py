def validate_fuel_amount(amount):
    """
    Validate fuel amount is valid.
    
    Args:
        amount: Amount to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        amount = float(amount)
    except (ValueError, TypeError):
        return False, "Amount must be a valid number"
    
    if amount <= 0:
        return False, "Amount must be positive"
    
    if amount > 10000:
        return False, "Amount exceeds maximum transfer limit (10000L)"
    
    return True, "Valid"


def validate_tank_id(tank_id):
    """
    Validate tank ID format.
    
    Args:
        tank_id: Tank ID to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    if not tank_id:
        return False, "Tank ID cannot be empty"
    
    if not isinstance(tank_id, str):
        return False, "Tank ID must be a string"
    
    if len(tank_id) > 50:
        return False, "Tank ID too long (max 50 characters)"
    
    return True, "Valid"


def validate_tank_capacity(capacity):
    """
    Validate tank capacity is reasonable.
    
    Args:
        capacity: Capacity to validate
    
    Returns:
        tuple: (is_valid, error_message)
    """
    try:
        capacity = float(capacity)
    except (ValueError, TypeError):
        return False, "Capacity must be a valid number"
    
    if capacity <= 0:
        return False, "Capacity must be positive"
    
    if capacity > 50000:
        return False, "Capacity exceeds maximum (50000L)"
    
    return True, "Valid"


def validate_pressure(pressure, max_pressure):
    """
    Validate pressure is within safe limits.
    
    Args:
        pressure: Current pressure
        max_pressure: Maximum allowed pressure
    
    Returns:
        tuple: (is_safe, warning_message)
    """
    if pressure <= max_pressure:
        return True, "Pressure within safe limits"
    
    overpressure = pressure - max_pressure
    return False, f"Pressure {overpressure:.1f} PSI above safe limit"


def validate_temperature(temperature, max_temperature):
    """
    Validate temperature is within safe limits.
    
    Args:
        temperature: Current temperature
        max_temperature: Maximum allowed temperature
    
    Returns:
        tuple: (is_safe, warning_message)
    """
    if temperature <= max_temperature:
        return True, "Temperature within safe limits"
    
    overtemp = temperature - max_temperature
    return False, f"Temperature {overtemp:.1f}°C above safe limit"


def validate_transfer_operation(source_tank, dest_tank, amount):
    """
    Comprehensive transfer validation.
    
    Args:
        source_tank: Source tank object
        dest_tank: Destination tank object
        amount: Amount to transfer
    
    Returns:
        tuple: (is_valid, error_message)
    """
    # Validate amount
    valid, msg = validate_fuel_amount(amount)
    if not valid:
        return False, msg
    
    # Check source has enough
    if source_tank.get_fuel_level() < amount:
        return False, f"Source has insufficient fuel ({source_tank.get_fuel_level():.1f}L available)"
    
    # Check destination has capacity
    if dest_tank.get_available_capacity() < amount:
        return False, f"Destination has insufficient capacity ({dest_tank.get_available_capacity():.1f}L available)"
    
    return True, "Transfer validated"


def sanitize_tank_name(name):
    """
    Sanitize tank name for display.
    
    Args:
        name: Tank name to sanitize
    
    Returns:
        Sanitized name
    """
    if not name:
        return "Unnamed Tank"
    
    # Remove extra whitespace
    name = " ".join(name.split())
    
    # Truncate if too long
    if len(name) > 100:
        name = name[:97] + "..."
    
    return name


def format_fuel_amount(amount):
    """
    Format fuel amount for display.
    
    Args:
        amount: Fuel amount
    
    Returns:
        Formatted string
    """
    try:
        amount = float(amount)
        return f"{amount:.1f}L"
    except:
        return "0.0L"


def format_percentage(percentage):
    """
    Format percentage for display.
    
    Args:
        percentage: Percentage value
    
    Returns:
        Formatted string
    """
    try:
        percentage = float(percentage)
        return f"{percentage:.1f}%"
    except:
        return "0.0%"
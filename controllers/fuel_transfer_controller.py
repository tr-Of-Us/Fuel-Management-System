class FuelTransferController:
    """Controller for managing fuel transfers between tanks"""
    
    def __init__(self, fuel_system, data_logger):
        """
        Initialize transfer controller.
        
        Args:
            fuel_system: FuelSystem instance
            data_logger: DataLogger instance
        """
        self._fuel_system = fuel_system
        self._logger = data_logger
    
    def validate_transfer(self, source_id, dest_id, amount):
        """
        Validate if transfer is safe and possible.
        
        Returns:
            tuple: (is_valid, error_message)
        """
        # Get tanks
        source = self._fuel_system.get_tank(source_id)
        dest = self._fuel_system.get_tank(dest_id)
        
        if not source:
            return False, f"Source tank {source_id} not found"
        if not dest:
            return False, f"Destination tank {dest_id} not found"
        
        # Same tank check
        if source_id == dest_id:
            return False, "Source and destination must be different"
        
        # Amount validation
        if amount <= 0:
            return False, "Amount must be positive"
        
        # Source has enough fuel
        if source.get_fuel_level() < amount:
            available = source.get_fuel_level()
            return False, f"Insufficient fuel in source (available: {available:.1f}L)"
        
        # Destination has capacity
        if dest.get_available_capacity() < amount:
            available = dest.get_available_capacity()
            return False, f"Insufficient capacity in destination (available: {available:.1f}L)"
        
        # Check reserve tank emergency mode
        if hasattr(source, 'is_emergency_mode'):
            if not source.is_emergency_mode():
                return False, "Reserve tank requires emergency mode activation"
        
        return True, "Valid"
    
    def execute_transfer(self, source_id, dest_id, amount):
        """
        Execute fuel transfer between tanks.
        
        Returns:
            tuple: (success, message)
        """
        # Validate first
        is_valid, message = self.validate_transfer(source_id, dest_id, amount)
        if not is_valid:
            self._logger.log_transfer(source_id, dest_id, amount, False)
            return False, message
        
        # Get tanks
        source = self._fuel_system.get_tank(source_id)
        dest = self._fuel_system.get_tank(dest_id)
        
        # Remove from source
        if not source.remove_fuel(amount):
            self._logger.log_transfer(source_id, dest_id, amount, False)
            return False, "Failed to remove fuel from source"
        
        # Add to destination
        if not dest.add_fuel(amount):
            # Rollback - add fuel back to source
            source.add_fuel(amount)
            self._logger.log_transfer(source_id, dest_id, amount, False)
            return False, "Failed to add fuel to destination (rolled back)"
        
        # Success
        self._logger.log_transfer(source_id, dest_id, amount, True)
        return True, f"Successfully transferred {amount:.1f}L"
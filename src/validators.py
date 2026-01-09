"""
Input validation utilities for trading bot.
Validates symbols, order sides, quantities, and prices.
"""

import re

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_symbol(symbol):
    """
    Validate trading symbol format.
    
    Args:
        symbol (str): Trading symbol (e.g., BTCUSDT)
        
    Returns:
        str: Uppercase validated symbol
        
    Raises:
        ValidationError: If symbol format is invalid
    """
    if not symbol or not isinstance(symbol, str):
        raise ValidationError("Symbol must be a non-empty string")
    
    symbol = symbol.upper()
    
    # Check if symbol matches expected pattern (letters/numbers only)
    if not re.match(r'^[A-Z0-9]+$', symbol):
        raise ValidationError(f"Invalid symbol format: {symbol}")
    
    # Common symbols should end with USDT for futures
    if not symbol.endswith('USDT'):
        raise ValidationError(f"Symbol should end with USDT for USDT-M Futures: {symbol}")
    
    return symbol

def validate_side(side):
    """
    Validate order side.
    
    Args:
        side (str): Order side (BUY or SELL)
        
    Returns:
        str: Uppercase validated side
        
    Raises:
        ValidationError: If side is not BUY or SELL
    """
    if not side or not isinstance(side, str):
        raise ValidationError("Side must be a non-empty string")
    
    side = side.upper()
    
    if side not in ['BUY', 'SELL']:
        raise ValidationError(f"Side must be BUY or SELL, got: {side}")
    
    return side

def validate_quantity(quantity):
    """
    Validate order quantity.
    
    Args:
        quantity: Order quantity (string or numeric)
        
    Returns:
        float: Validated quantity
        
    Raises:
        ValidationError: If quantity is invalid or non-positive
    """
    try:
        qty = float(quantity)
    except (ValueError, TypeError):
        raise ValidationError(f"Quantity must be a number, got: {quantity}")
    
    if qty <= 0:
        raise ValidationError(f"Quantity must be greater than 0, got: {qty}")
    
    return qty

def validate_price(price, price_type="price"):
    """
    Validate price value.
    
    Args:
        price: Price value (string or numeric)
        price_type (str): Type of price for error messages
        
    Returns:
        float: Validated price
        
    Raises:
        ValidationError: If price is invalid or non-positive
    """
    try:
        price_val = float(price)
    except (ValueError, TypeError):
        raise ValidationError(f"{price_type.capitalize()} must be a number, got: {price}")
    
    if price_val <= 0:
        raise ValidationError(f"{price_type.capitalize()} must be greater than 0, got: {price_val}")
    
    return price_val

def validate_stop_limit_prices(stop_price, limit_price, side):
    """
    Validate stop and limit prices for stop-limit orders.
    
    Args:
        stop_price (float): Stop trigger price
        limit_price (float): Limit order price
        side (str): Order side (BUY or SELL)
        
    Raises:
        ValidationError: If price relationship is incorrect
    """
    if side == 'BUY':
        # For buy stop-limit: stop price should be >= limit price
        if stop_price < limit_price:
            raise ValidationError(
                f"For BUY stop-limit: stop price ({stop_price}) should be >= limit price ({limit_price})"
            )
    else:  # SELL
        # For sell stop-limit: stop price should be <= limit price
        if stop_price > limit_price:
            raise ValidationError(
                f"For SELL stop-limit: stop price ({stop_price}) should be <= limit price ({limit_price})"
            )

def validate_positive_integer(value, name):
    """
    Validate positive integer value.
    
    Args:
        value: Value to validate
        name (str): Parameter name for error messages
        
    Returns:
        int: Validated integer
        
    Raises:
        ValidationError: If value is not a positive integer
    """
    try:
        int_val = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f"{name} must be an integer, got: {value}")
    
    if int_val <= 0:
        raise ValidationError(f"{name} must be greater than 0, got: {int_val}")
    
    return int_val

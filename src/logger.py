"""
Structured logging configuration for the trading bot.
Logs are written to bot.log with timestamp, level, and detailed information.
"""

import logging
import sys
from datetime import datetime

def setup_logger(name='TradingBot'):
    """
    Configure and return a logger instance with file and console handlers.
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    
    # Avoid duplicate handlers
    if logger.handlers:
        return logger
    
    # File handler
    file_handler = logging.FileHandler('bot.log', mode='a')
    file_handler.setLevel(logging.DEBUG)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

def log_order(logger, order_type, symbol, side, quantity, price=None, stop_price=None, response=None, error=None):
    """
    Log order details in a structured format.
    
    Args:
        logger: Logger instance
        order_type (str): Type of order (MARKET, LIMIT, STOP_LIMIT, etc.)
        symbol (str): Trading symbol
        side (str): BUY or SELL
        quantity (float): Order quantity
        price (float, optional): Limit price
        stop_price (float, optional): Stop price
        response (dict, optional): API response
        error (Exception, optional): Error if any
    """
    log_msg = f"Order Type: {order_type} | Symbol: {symbol} | Side: {side} | Quantity: {quantity}"
    
    if price:
        log_msg += f" | Price: {price}"
    if stop_price:
        log_msg += f" | Stop Price: {stop_price}"
    
    if error:
        logger.error(f"{log_msg} | Status: FAILED | Error: {str(error)}", exc_info=True)
    elif response:
        order_id = response.get('orderId', 'N/A')
        status = response.get('status', 'N/A')
        logger.info(f"{log_msg} | Status: {status} | Order ID: {order_id}")
    else:
        logger.info(log_msg)

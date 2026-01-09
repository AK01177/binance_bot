"""
Stop-Limit order execution for Binance Futures.
Places orders that trigger at a stop price and execute at limit price.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance.exceptions import BinanceAPIException
from client import get_binance_client
from validators import (
    validate_symbol, validate_side, validate_quantity, 
    validate_price, validate_stop_limit_prices, ValidationError
)
from logger import setup_logger, log_order

logger = setup_logger('StopLimitOrders')

def place_stop_limit_order(symbol, side, quantity, stop_price, limit_price):
    """
    Place a stop-limit order on Binance Futures Testnet.
    
    Args:
        symbol (str): Trading symbol (e.g., BTCUSDT)
        side (str): Order side (BUY or SELL)
        quantity (float): Order quantity
        stop_price (float): Stop trigger price
        limit_price (float): Limit order price
        
    Returns:
        dict: API response with order details
        
    Raises:
        ValidationError: If input validation fails
        BinanceAPIException: If API call fails
    """
    # Validate inputs
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    quantity = validate_quantity(quantity)
    stop_price = validate_price(stop_price, "stop price")
    limit_price = validate_price(limit_price, "limit price")
    
    # Validate price relationship
    validate_stop_limit_prices(stop_price, limit_price, side)
    
    logger.info(f"Placing stop-limit order: {side} {quantity} {symbol} @ stop={stop_price}, limit={limit_price}")
    
    try:
        # Get authenticated client
        client = get_binance_client()
        
        # Place stop-limit order
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='STOP',
            timeInForce='GTC',
            quantity=quantity,
            price=limit_price,
            stopPrice=stop_price
        )
        
        # Log successful order
        log_order(
            logger=logger,
            order_type='STOP_LIMIT',
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=limit_price,
            stop_price=stop_price,
            response=order
        )
        
        return order
        
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e}", exc_info=True)
        log_order(
            logger=logger,
            order_type='STOP_LIMIT',
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=limit_price,
            stop_price=stop_price,
            error=e
        )
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error placing stop-limit order: {e}", exc_info=True)
        log_order(
            logger=logger,
            order_type='STOP_LIMIT',
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=limit_price,
            stop_price=stop_price,
            error=e
        )
        raise

def main():
    """CLI entry point for stop-limit orders."""
    if len(sys.argv) != 6:
        print("Usage: python stop_limit.py <SYMBOL> <SIDE> <QUANTITY> <STOP_PRICE> <LIMIT_PRICE>")
        print("Example: python stop_limit.py BTCUSDT BUY 0.01 44000 44500")
        print("\nNote:")
        print("  - For BUY: stop_price should be >= limit_price")
        print("  - For SELL: stop_price should be <= limit_price")
        sys.exit(1)
    
    symbol = sys.argv[1]
    side = sys.argv[2]
    quantity = sys.argv[3]
    stop_price = sys.argv[4]
    limit_price = sys.argv[5]
    
    try:
        order = place_stop_limit_order(symbol, side, quantity, stop_price, limit_price)
        
        print("\n✓ Stop-limit order placed successfully!")
        print(f"Order ID: {order.get('orderId')}")
        print(f"Symbol: {order.get('symbol')}")
        print(f"Side: {order.get('side')}")
        print(f"Quantity: {order.get('origQty')}")
        print(f"Stop Price: {order.get('stopPrice')}")
        print(f"Limit Price: {order.get('price')}")
        print(f"Status: {order.get('status')}")
        
    except ValidationError as e:
        print(f"\n✗ Validation Error: {e}")
        logger.error(f"Validation error: {e}")
        sys.exit(1)
        
    except BinanceAPIException as e:
        print(f"\n✗ Binance API Error: {e}")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

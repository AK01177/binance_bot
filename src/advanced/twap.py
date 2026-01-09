"""
Time-Weighted Average Price (TWAP) strategy for Binance Futures.
Splits a large order into smaller chunks executed at regular intervals.
"""

import sys
import os
import time
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance.exceptions import BinanceAPIException
from client import get_binance_client
from validators import (
    validate_symbol, validate_side, validate_quantity, 
    validate_positive_integer, ValidationError
)
from logger import setup_logger, log_order

logger = setup_logger('TWAP')

def execute_twap(symbol, side, total_quantity, num_orders, interval_seconds):
    """
    Execute a TWAP strategy by splitting orders over time.
    
    Args:
        symbol (str): Trading symbol (e.g., BTCUSDT)
        side (str): Order side (BUY or SELL)
        total_quantity (float): Total quantity to trade
        num_orders (int): Number of orders to split into
        interval_seconds (int): Seconds between each order
        
    Returns:
        list: List of all executed orders
        
    Raises:
        ValidationError: If input validation fails
        BinanceAPIException: If API call fails
    """
    # Validate inputs
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    total_quantity = validate_quantity(total_quantity)
    num_orders = validate_positive_integer(num_orders, "number of orders")
    interval_seconds = validate_positive_integer(interval_seconds, "interval seconds")
    
    # Calculate quantity per order
    quantity_per_order = total_quantity / num_orders
    
    logger.info(f"Starting TWAP strategy: {side} {total_quantity} {symbol}")
    logger.info(f"  Split into {num_orders} orders of {quantity_per_order} each")
    logger.info(f"  Interval: {interval_seconds} seconds")
    
    executed_orders = []
    
    try:
        client = get_binance_client()
        
        for i in range(num_orders):
            try:
                # Place market order for this chunk
                order = client.futures_create_order(
                    symbol=symbol,
                    side=side,
                    type='MARKET',
                    quantity=quantity_per_order
                )
                
                executed_orders.append(order)
                
                logger.info(f"TWAP order {i+1}/{num_orders} executed: {order.get('orderId')}")
                print(f"✓ Order {i+1}/{num_orders} executed - ID: {order.get('orderId')}")
                
                # Wait before next order (except for the last one)
                if i < num_orders - 1:
                    logger.info(f"Waiting {interval_seconds} seconds before next order...")
                    print(f"  Waiting {interval_seconds} seconds...")
                    time.sleep(interval_seconds)
                    
            except BinanceAPIException as e:
                logger.error(f"Error on TWAP order {i+1}/{num_orders}: {e}", exc_info=True)
                print(f"✗ Error on order {i+1}/{num_orders}: {e}")
                # Continue with remaining orders
                
        # Log overall TWAP execution
        log_order(
            logger=logger,
            order_type='TWAP',
            symbol=symbol,
            side=side,
            quantity=total_quantity,
            response={'executed_orders': len(executed_orders), 'total_orders': num_orders}
        )
        
        return executed_orders
        
    except Exception as e:
        logger.error(f"Unexpected error in TWAP execution: {e}", exc_info=True)
        log_order(
            logger=logger,
            order_type='TWAP',
            symbol=symbol,
            side=side,
            quantity=total_quantity,
            error=e
        )
        raise

def main():
    """CLI entry point for TWAP strategy."""
    if len(sys.argv) != 6:
        print("Usage: python twap.py <SYMBOL> <SIDE> <TOTAL_QUANTITY> <NUM_ORDERS> <INTERVAL_SECONDS>")
        print("Example: python twap.py BTCUSDT BUY 0.1 10 30")
        print("\nThis will:")
        print("  - Split 0.1 BTC into 10 orders of 0.01 BTC each")
        print("  - Execute one order every 30 seconds")
        sys.exit(1)
    
    symbol = sys.argv[1]
    side = sys.argv[2]
    total_quantity = sys.argv[3]
    num_orders = sys.argv[4]
    interval_seconds = sys.argv[5]
    
    try:
        print(f"\nStarting TWAP execution...")
        print(f"Total quantity: {total_quantity} {symbol}")
        print(f"Split into: {num_orders} orders")
        print(f"Interval: {interval_seconds} seconds\n")
        
        orders = execute_twap(symbol, side, total_quantity, num_orders, interval_seconds)
        
        print(f"\n✓ TWAP execution completed!")
        print(f"Successfully executed: {len(orders)}/{num_orders} orders")
        
        # Calculate average price if available
        total_qty = 0
        total_cost = 0
        for order in orders:
            if 'avgPrice' in order and order['avgPrice']:
                qty = float(order.get('executedQty', 0))
                price = float(order['avgPrice'])
                total_qty += qty
                total_cost += qty * price
        
        if total_qty > 0:
            avg_price = total_cost / total_qty
            print(f"Average execution price: {avg_price:.2f}")
        
    except ValidationError as e:
        print(f"\n✗ Validation Error: {e}")
        logger.error(f"Validation error: {e}")
        sys.exit(1)
        
    except BinanceAPIException as e:
        print(f"\n✗ Binance API Error: {e}")
        sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\n✗ TWAP execution interrupted by user")
        logger.info("TWAP execution interrupted by user")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

"""
Order management utilities for viewing and canceling orders.
Provides helper functions to manage active orders.
"""

import sys
from binance.exceptions import BinanceAPIException
from client import get_binance_client
from validators import validate_symbol, ValidationError
from logger import setup_logger

logger = setup_logger('OrderManager')

def get_open_orders(symbol=None):
    """
    Get all open orders or orders for a specific symbol.
    
    Args:
        symbol (str, optional): Trading symbol to filter by
        
    Returns:
        list: List of open orders
    """
    try:
        client = get_binance_client()
        
        if symbol:
            symbol = validate_symbol(symbol)
            orders = client.futures_get_open_orders(symbol=symbol)
            logger.info(f"Retrieved {len(orders)} open orders for {symbol}")
        else:
            orders = client.futures_get_open_orders()
            logger.info(f"Retrieved {len(orders)} open orders")
        
        return orders
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error getting open orders: {e}", exc_info=True)
        raise

def cancel_order(symbol, order_id):
    """
    Cancel a specific order.
    
    Args:
        symbol (str): Trading symbol
        order_id (int): Order ID to cancel
        
    Returns:
        dict: Cancellation response
    """
    try:
        symbol = validate_symbol(symbol)
        client = get_binance_client()
        
        result = client.futures_cancel_order(
            symbol=symbol,
            orderId=order_id
        )
        
        logger.info(f"Cancelled order {order_id} for {symbol}")
        return result
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error cancelling order: {e}", exc_info=True)
        raise

def cancel_all_orders(symbol):
    """
    Cancel all open orders for a symbol.
    
    Args:
        symbol (str): Trading symbol
        
    Returns:
        list: List of cancelled orders
    """
    try:
        symbol = validate_symbol(symbol)
        client = get_binance_client()
        
        result = client.futures_cancel_all_open_orders(symbol=symbol)
        
        logger.info(f"Cancelled all orders for {symbol}")
        return result
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error cancelling all orders: {e}", exc_info=True)
        raise

def get_order_status(symbol, order_id):
    """
    Get the status of a specific order.
    
    Args:
        symbol (str): Trading symbol
        order_id (int): Order ID
        
    Returns:
        dict: Order information
    """
    try:
        symbol = validate_symbol(symbol)
        client = get_binance_client()
        
        order = client.futures_get_order(
            symbol=symbol,
            orderId=order_id
        )
        
        logger.info(f"Retrieved status for order {order_id}")
        return order
        
    except ValidationError as e:
        logger.error(f"Validation error: {e}")
        raise
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error getting order status: {e}", exc_info=True)
        raise

def display_orders(orders):
    """
    Display orders in a formatted table.
    
    Args:
        orders (list): List of order dictionaries
    """
    if not orders:
        print("No orders found.")
        return
    
    print(f"\nTotal Orders: {len(orders)}")
    print("-" * 100)
    print(f"{'ID':<15} {'Symbol':<10} {'Side':<6} {'Type':<10} {'Quantity':<12} {'Price':<12} {'Status':<10}")
    print("-" * 100)
    
    for order in orders:
        order_id = str(order.get('orderId', 'N/A'))
        symbol = order.get('symbol', 'N/A')
        side = order.get('side', 'N/A')
        order_type = order.get('type', 'N/A')
        quantity = order.get('origQty', 'N/A')
        price = order.get('price', 'MARKET')
        status = order.get('status', 'N/A')
        
        print(f"{order_id:<15} {symbol:<10} {side:<6} {order_type:<10} {quantity:<12} {price:<12} {status:<10}")

def main():
    """CLI entry point for order management."""
    if len(sys.argv) < 2:
        print("Order Management Utilities")
        print("\nUsage:")
        print("  python order_manager.py list [SYMBOL]           - List open orders")
        print("  python order_manager.py cancel <SYMBOL> <ID>    - Cancel specific order")
        print("  python order_manager.py cancel_all <SYMBOL>     - Cancel all orders for symbol")
        print("  python order_manager.py status <SYMBOL> <ID>    - Get order status")
        print("\nExamples:")
        print("  python order_manager.py list")
        print("  python order_manager.py list BTCUSDT")
        print("  python order_manager.py cancel BTCUSDT 12345678")
        print("  python order_manager.py cancel_all BTCUSDT")
        print("  python order_manager.py status BTCUSDT 12345678")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    try:
        if command == "list":
            symbol = sys.argv[2] if len(sys.argv) > 2 else None
            orders = get_open_orders(symbol)
            display_orders(orders)
            
        elif command == "cancel":
            if len(sys.argv) != 4:
                print("Usage: python order_manager.py cancel <SYMBOL> <ORDER_ID>")
                sys.exit(1)
            
            symbol = sys.argv[2]
            order_id = int(sys.argv[3])
            result = cancel_order(symbol, order_id)
            print(f"✓ Order {order_id} cancelled successfully")
            
        elif command == "cancel_all":
            if len(sys.argv) != 3:
                print("Usage: python order_manager.py cancel_all <SYMBOL>")
                sys.exit(1)
            
            symbol = sys.argv[2]
            result = cancel_all_orders(symbol)
            print(f"✓ All orders for {symbol} cancelled successfully")
            
        elif command == "status":
            if len(sys.argv) != 4:
                print("Usage: python order_manager.py status <SYMBOL> <ORDER_ID>")
                sys.exit(1)
            
            symbol = sys.argv[2]
            order_id = int(sys.argv[3])
            order = get_order_status(symbol, order_id)
            
            print(f"\nOrder Details:")
            print(f"  Order ID: {order.get('orderId')}")
            print(f"  Symbol: {order.get('symbol')}")
            print(f"  Side: {order.get('side')}")
            print(f"  Type: {order.get('type')}")
            print(f"  Status: {order.get('status')}")
            print(f"  Original Qty: {order.get('origQty')}")
            print(f"  Executed Qty: {order.get('executedQty')}")
            print(f"  Price: {order.get('price')}")
            if order.get('stopPrice'):
                print(f"  Stop Price: {order.get('stopPrice')}")
            
        else:
            print(f"Unknown command: {command}")
            sys.exit(1)
            
    except ValidationError as e:
        print(f"✗ Validation Error: {e}")
        sys.exit(1)
    except BinanceAPIException as e:
        print(f"✗ Binance API Error: {e}")
        sys.exit(1)
    except ValueError:
        print(f"✗ Invalid order ID. Must be a number.")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

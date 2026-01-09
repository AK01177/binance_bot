"""
Limit order execution for Binance Futures.
Supports BUY and SELL limit orders with price specification.
"""

import sys
from binance.exceptions import BinanceAPIException
from client import get_binance_client
from validators import validate_symbol, validate_side, validate_quantity, validate_price, ValidationError
from logger import setup_logger, log_order

logger = setup_logger('LimitOrders')

def place_limit_order(symbol, side, quantity, price):
    """
    Place a limit order on Binance Futures Testnet.
    
    Args:
        symbol (str): Trading symbol (e.g., BTCUSDT)
        side (str): Order side (BUY or SELL)
        quantity (float): Order quantity
        price (float): Limit price
        
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
    price = validate_price(price, "limit price")
    
    logger.info(f"Placing limit order: {side} {quantity} {symbol} @ {price}")
    
    try:
        # Get authenticated client
        client = get_binance_client()
        
        # Place limit order
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='LIMIT',
            timeInForce='GTC',  # Good Till Cancel
            quantity=quantity,
            price=price
        )
        
        # Log successful order
        log_order(
            logger=logger,
            order_type='LIMIT',
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            response=order
        )
        
        return order
        
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e}", exc_info=True)
        log_order(
            logger=logger,
            order_type='LIMIT',
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            error=e
        )
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error placing limit order: {e}", exc_info=True)
        log_order(
            logger=logger,
            order_type='LIMIT',
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            error=e
        )
        raise

def main():
    """CLI entry point for limit orders."""
    if len(sys.argv) != 5:
        print("Usage: python limit_orders.py <SYMBOL> <SIDE> <QUANTITY> <PRICE>")
        print("Example: python limit_orders.py BTCUSDT SELL 0.01 45000")
        sys.exit(1)
    
    symbol = sys.argv[1]
    side = sys.argv[2]
    quantity = sys.argv[3]
    price = sys.argv[4]
    
    try:
        order = place_limit_order(symbol, side, quantity, price)
        
        print("\n✓ Limit order placed successfully!")
        print(f"Order ID: {order.get('orderId')}")
        print(f"Symbol: {order.get('symbol')}")
        print(f"Side: {order.get('side')}")
        print(f"Quantity: {order.get('origQty')}")
        print(f"Price: {order.get('price')}")
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

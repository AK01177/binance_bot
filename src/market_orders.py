"""
Market order execution for Binance Futures.
Supports BUY and SELL market orders with validation and logging.
"""

import sys
from binance.exceptions import BinanceAPIException
from client import get_binance_client
from validators import validate_symbol, validate_side, validate_quantity, ValidationError
from logger import setup_logger, log_order

logger = setup_logger('MarketOrders')

def place_market_order(symbol, side, quantity):
    """
    Place a market order on Binance Futures Testnet.
    
    Args:
        symbol (str): Trading symbol (e.g., BTCUSDT)
        side (str): Order side (BUY or SELL)
        quantity (float): Order quantity
        
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
    
    logger.info(f"Placing market order: {side} {quantity} {symbol}")
    
    try:
        # Get authenticated client
        client = get_binance_client()
        
        # Place market order
        order = client.futures_create_order(
            symbol=symbol,
            side=side,
            type='MARKET',
            quantity=quantity
        )
        
        # Log successful order
        log_order(
            logger=logger,
            order_type='MARKET',
            symbol=symbol,
            side=side,
            quantity=quantity,
            response=order
        )
        
        return order
        
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e}", exc_info=True)
        log_order(
            logger=logger,
            order_type='MARKET',
            symbol=symbol,
            side=side,
            quantity=quantity,
            error=e
        )
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error placing market order: {e}", exc_info=True)
        log_order(
            logger=logger,
            order_type='MARKET',
            symbol=symbol,
            side=side,
            quantity=quantity,
            error=e
        )
        raise

def main():
    """CLI entry point for market orders."""
    if len(sys.argv) != 4:
        print("Usage: python market_orders.py <SYMBOL> <SIDE> <QUANTITY>")
        print("Example: python market_orders.py BTCUSDT BUY 0.01")
        sys.exit(1)
    
    symbol = sys.argv[1]
    side = sys.argv[2]
    quantity = sys.argv[3]
    
    try:
        order = place_market_order(symbol, side, quantity)
        
        print("\n✓ Market order placed successfully!")
        print(f"Order ID: {order.get('orderId')}")
        print(f"Symbol: {order.get('symbol')}")
        print(f"Side: {order.get('side')}")
        print(f"Quantity: {order.get('executedQty')}")
        print(f"Status: {order.get('status')}")
        
        if 'avgPrice' in order and order['avgPrice']:
            print(f"Average Price: {order.get('avgPrice')}")
        
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

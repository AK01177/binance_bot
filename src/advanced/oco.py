"""
One-Cancels-the-Other (OCO) order execution for Binance Futures.
Places two orders where execution of one cancels the other.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance.exceptions import BinanceAPIException
from client import get_binance_client
from validators import (
    validate_symbol, validate_side, validate_quantity, 
    validate_price, ValidationError
)
from logger import setup_logger, log_order

logger = setup_logger('OCOOrders')

def place_oco_order(symbol, side, quantity, price, stop_price, stop_limit_price):
    """
    Place an OCO order on Binance Futures Testnet.
    
    Note: OCO orders on Futures work differently than spot.
    This implementation creates a limit order and a stop-limit order manually.
    
    Args:
        symbol (str): Trading symbol (e.g., BTCUSDT)
        side (str): Order side (BUY or SELL)
        quantity (float): Order quantity
        price (float): Limit order price (take profit)
        stop_price (float): Stop trigger price (stop loss)
        stop_limit_price (float): Stop limit order price
        
    Returns:
        dict: Dictionary with both order responses
        
    Raises:
        ValidationError: If input validation fails
        BinanceAPIException: If API call fails
    """
    # Validate inputs
    symbol = validate_symbol(symbol)
    side = validate_side(side)
    quantity = validate_quantity(quantity)
    price = validate_price(price, "limit price")
    stop_price = validate_price(stop_price, "stop price")
    stop_limit_price = validate_price(stop_limit_price, "stop limit price")
    
    logger.info(f"Placing OCO order: {side} {quantity} {symbol}")
    logger.info(f"  Take Profit: {price}, Stop Loss: {stop_price}/{stop_limit_price}")
    
    try:
        client = get_binance_client()
        
        # Determine opposite side for closing position
        close_side = 'SELL' if side == 'BUY' else 'BUY'
        
        # Place take profit limit order
        take_profit = client.futures_create_order(
            symbol=symbol,
            side=close_side,
            type='TAKE_PROFIT',
            timeInForce='GTC',
            quantity=quantity,
            price=price,
            stopPrice=price,
            reduceOnly='true'
        )
        
        logger.info(f"Take profit order placed: {take_profit.get('orderId')}")
        
        # Place stop loss order
        stop_loss = client.futures_create_order(
            symbol=symbol,
            side=close_side,
            type='STOP',
            timeInForce='GTC',
            quantity=quantity,
            price=stop_limit_price,
            stopPrice=stop_price,
            reduceOnly='true'
        )
        
        logger.info(f"Stop loss order placed: {stop_loss.get('orderId')}")
        
        result = {
            'take_profit': take_profit,
            'stop_loss': stop_loss
        }
        
        log_order(
            logger=logger,
            order_type='OCO',
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            response=result
        )
        
        return result
        
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e}", exc_info=True)
        log_order(
            logger=logger,
            order_type='OCO',
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            error=e
        )
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error placing OCO order: {e}", exc_info=True)
        log_order(
            logger=logger,
            order_type='OCO',
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=price,
            stop_price=stop_price,
            error=e
        )
        raise

def main():
    """CLI entry point for OCO orders."""
    if len(sys.argv) != 7:
        print("Usage: python oco.py <SYMBOL> <SIDE> <QUANTITY> <TAKE_PROFIT_PRICE> <STOP_PRICE> <STOP_LIMIT_PRICE>")
        print("Example: python oco.py BTCUSDT BUY 0.01 46000 43000 42900")
        print("\nThis creates:")
        print("  - Take profit order at TAKE_PROFIT_PRICE")
        print("  - Stop loss order triggered at STOP_PRICE, executed at STOP_LIMIT_PRICE")
        sys.exit(1)
    
    symbol = sys.argv[1]
    side = sys.argv[2]
    quantity = sys.argv[3]
    price = sys.argv[4]
    stop_price = sys.argv[5]
    stop_limit_price = sys.argv[6]
    
    try:
        result = place_oco_order(symbol, side, quantity, price, stop_price, stop_limit_price)
        
        print("\n✓ OCO orders placed successfully!")
        print("\nTake Profit Order:")
        print(f"  Order ID: {result['take_profit'].get('orderId')}")
        print(f"  Price: {result['take_profit'].get('price')}")
        print(f"  Status: {result['take_profit'].get('status')}")
        
        print("\nStop Loss Order:")
        print(f"  Order ID: {result['stop_loss'].get('orderId')}")
        print(f"  Stop Price: {result['stop_loss'].get('stopPrice')}")
        print(f"  Limit Price: {result['stop_loss'].get('price')}")
        print(f"  Status: {result['stop_loss'].get('status')}")
        
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

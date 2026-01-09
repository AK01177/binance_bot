"""
Grid Trading Strategy for Binance Futures.
Places multiple buy and sell limit orders at predetermined price levels.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from binance.exceptions import BinanceAPIException
from client import get_binance_client
from validators import (
    validate_symbol, validate_quantity, validate_price,
    validate_positive_integer, ValidationError
)
from logger import setup_logger, log_order

logger = setup_logger('GridStrategy')

def setup_grid_strategy(symbol, quantity_per_grid, lower_price, upper_price, num_grids):
    """
    Set up a grid trading strategy with buy and sell orders.
    
    Args:
        symbol (str): Trading symbol (e.g., BTCUSDT)
        quantity_per_grid (float): Quantity for each grid level
        lower_price (float): Lower bound price
        upper_price (float): Upper bound price
        num_grids (int): Number of grid levels
        
    Returns:
        dict: Dictionary with buy and sell orders
        
    Raises:
        ValidationError: If input validation fails
        BinanceAPIException: If API call fails
    """
    # Validate inputs
    symbol = validate_symbol(symbol)
    quantity_per_grid = validate_quantity(quantity_per_grid)
    lower_price = validate_price(lower_price, "lower price")
    upper_price = validate_price(upper_price, "upper price")
    num_grids = validate_positive_integer(num_grids, "number of grids")
    
    if upper_price <= lower_price:
        raise ValidationError(f"Upper price ({upper_price}) must be greater than lower price ({lower_price})")
    
    # Calculate grid levels
    price_step = (upper_price - lower_price) / (num_grids - 1)
    grid_prices = [lower_price + i * price_step for i in range(num_grids)]
    
    logger.info(f"Setting up grid strategy for {symbol}")
    logger.info(f"  Price range: {lower_price} - {upper_price}")
    logger.info(f"  Grid levels: {num_grids}")
    logger.info(f"  Price step: {price_step}")
    logger.info(f"  Quantity per grid: {quantity_per_grid}")
    
    try:
        client = get_binance_client()
        
        # Get current market price
        ticker = client.futures_symbol_ticker(symbol=symbol)
        current_price = float(ticker['price'])
        logger.info(f"Current market price: {current_price}")
        
        buy_orders = []
        sell_orders = []
        
        # Place grid orders
        for i, price in enumerate(grid_prices):
            try:
                if price < current_price:
                    # Place buy order below current price
                    order = client.futures_create_order(
                        symbol=symbol,
                        side='BUY',
                        type='LIMIT',
                        timeInForce='GTC',
                        quantity=quantity_per_grid,
                        price=price
                    )
                    buy_orders.append(order)
                    logger.info(f"Buy order placed at {price}: {order.get('orderId')}")
                    print(f"✓ Buy order {len(buy_orders)} placed at {price}")
                    
                elif price > current_price:
                    # Place sell order above current price
                    order = client.futures_create_order(
                        symbol=symbol,
                        side='SELL',
                        type='LIMIT',
                        timeInForce='GTC',
                        quantity=quantity_per_grid,
                        price=price
                    )
                    sell_orders.append(order)
                    logger.info(f"Sell order placed at {price}: {order.get('orderId')}")
                    print(f"✓ Sell order {len(sell_orders)} placed at {price}")
                    
            except BinanceAPIException as e:
                logger.error(f"Error placing grid order at {price}: {e}")
                print(f"✗ Error at price {price}: {e}")
                # Continue with remaining orders
        
        result = {
            'buy_orders': buy_orders,
            'sell_orders': sell_orders,
            'grid_prices': grid_prices,
            'current_price': current_price
        }
        
        log_order(
            logger=logger,
            order_type='GRID',
            symbol=symbol,
            side='BOTH',
            quantity=quantity_per_grid * num_grids,
            response={'buy_count': len(buy_orders), 'sell_count': len(sell_orders)}
        )
        
        return result
        
    except BinanceAPIException as e:
        logger.error(f"Binance API error: {e}", exc_info=True)
        log_order(
            logger=logger,
            order_type='GRID',
            symbol=symbol,
            side='BOTH',
            quantity=quantity_per_grid * num_grids,
            error=e
        )
        raise
        
    except Exception as e:
        logger.error(f"Unexpected error in grid strategy: {e}", exc_info=True)
        log_order(
            logger=logger,
            order_type='GRID',
            symbol=symbol,
            side='BOTH',
            quantity=quantity_per_grid * num_grids,
            error=e
        )
        raise

def main():
    """CLI entry point for grid strategy."""
    if len(sys.argv) != 6:
        print("Usage: python grid_strategy.py <SYMBOL> <QUANTITY_PER_GRID> <LOWER_PRICE> <UPPER_PRICE> <NUM_GRIDS>")
        print("Example: python grid_strategy.py BTCUSDT 0.01 43000 47000 10")
        print("\nThis will:")
        print("  - Create 10 grid levels between 43000 and 47000")
        print("  - Place buy orders below current price")
        print("  - Place sell orders above current price")
        print("  - Each order will be for 0.01 BTC")
        sys.exit(1)
    
    symbol = sys.argv[1]
    quantity_per_grid = sys.argv[2]
    lower_price = sys.argv[3]
    upper_price = sys.argv[4]
    num_grids = sys.argv[5]
    
    try:
        print(f"\nSetting up grid strategy for {symbol}...")
        print(f"Price range: {lower_price} - {upper_price}")
        print(f"Grid levels: {num_grids}")
        print(f"Quantity per grid: {quantity_per_grid}\n")
        
        result = setup_grid_strategy(symbol, quantity_per_grid, lower_price, upper_price, num_grids)
        
        print(f"\n✓ Grid strategy setup completed!")
        print(f"Current market price: {result['current_price']}")
        print(f"Buy orders placed: {len(result['buy_orders'])}")
        print(f"Sell orders placed: {len(result['sell_orders'])}")
        print(f"Total orders: {len(result['buy_orders']) + len(result['sell_orders'])}")
        
        print("\nGrid price levels:")
        for i, price in enumerate(result['grid_prices'], 1):
            marker = "→" if abs(price - result['current_price']) < (result['grid_prices'][1] - result['grid_prices'][0]) else " "
            print(f"  {marker} Level {i}: {price:.2f}")
        
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

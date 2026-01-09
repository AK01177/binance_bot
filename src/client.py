"""
Binance Futures Testnet client configuration.
Handles API authentication and connection setup.
"""

import os
from binance.client import Client
from binance.exceptions import BinanceAPIException
from dotenv import load_dotenv
from logger import setup_logger

# Load environment variables
load_dotenv()

logger = setup_logger('BinanceClient')

def get_binance_client():
    """
    Initialize and return Binance Futures Testnet client.
    
    Returns:
        Client: Authenticated Binance client instance
        
    Raises:
        Exception: If API credentials are missing or invalid
    """
    # Get credentials from environment
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    
    if not api_key or not api_secret:
        error_msg = "Missing API credentials. Set BINANCE_API_KEY and BINANCE_API_SECRET environment variables."
        logger.error(error_msg)
        raise Exception(error_msg)
    
    try:
        # Initialize client with testnet enabled
        client = Client(api_key, api_secret, testnet=True)
        
        # Test connection
        client.futures_ping()
        
        logger.info("Successfully connected to Binance Futures Testnet")
        return client
        
    except BinanceAPIException as e:
        logger.error(f"Binance API error during client initialization: {e}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Error initializing Binance client: {e}", exc_info=True)
        raise

def test_connection():
    """
    Test the connection to Binance Futures Testnet.
    
    Returns:
        bool: True if connection successful
    """
    try:
        client = get_binance_client()
        
        # Get account information to verify authentication
        account = client.futures_account()
        balance = float(account.get('totalWalletBalance', 0))
        
        logger.info(f"Connection test successful. Account balance: {balance} USDT")
        return True
        
    except Exception as e:
        logger.error(f"Connection test failed: {e}")
        return False

if __name__ == "__main__":
    # Run connection test when script is executed directly
    print("Testing Binance Futures Testnet connection...")
    if test_connection():
        print("✓ Connection successful!")
    else:
        print("✗ Connection failed. Check your API credentials and network.")

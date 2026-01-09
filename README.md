# Binance Futures Trading Bot

A professional CLI-based trading bot for Binance USDT-M Futures Testnet with support for market orders, limit orders, and advanced trading strategies.

## 📌 Features

### ✅ Mandatory Features
- **Market Orders**: Instant execution at current market price
- **Limit Orders**: Execute at specified price levels
- **Order Sides**: Support for both BUY and SELL
- **Binance Testnet**: Safe testing environment with virtual funds
- **CLI Interface**: Easy-to-use command-line interface
- **Input Validation**: Robust validation for all parameters
- **Structured Logging**: Detailed logs in `bot.log`
- **Error Handling**: Comprehensive exception handling with tracebacks

### ⭐ Bonus Features
- **Stop-Limit Orders**: Trigger orders at stop price, execute at limit price
- **OCO (One-Cancels-the-Other)**: Simultaneous take-profit and stop-loss orders
- **TWAP Strategy**: Time-Weighted Average Price execution
- **Grid Trading**: Automated grid strategy with multiple price levels

## 📁 Project Structure

```
binance_bot/
│
├── src/
│   ├── client.py               # Binance client setup (testnet)
│   ├── market_orders.py        # Market order logic
│   ├── limit_orders.py         # Limit order logic
│   ├── validators.py           # Input validation utilities
│   ├── logger.py               # Logging configuration
│   │
│   └── advanced/               # Advanced strategies
│       ├── stop_limit.py       # Stop-limit orders
│       ├── oco.py              # One-Cancels-the-Other
│       ├── twap.py             # Time-Weighted Average Price
│       └── grid_strategy.py    # Grid trading strategy
│
├── bot.log                     # Execution logs
├── requirements.txt            # Python dependencies
├── .env                        # API credentials (not committed)
└── README.md                   # This file
```

## ⚙️ Setup Instructions

### 1️⃣ Binance Testnet Account

1. Register at: https://testnet.binancefuture.com
2. Generate API Key and Secret from the account page
3. Enable Futures trading (should be enabled by default on testnet)

### 2️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies:**
- `python-binance==1.0.19` - Official Binance API wrapper
- `requests==2.31.0` - HTTP library
- `python-dotenv==1.0.0` - Environment variable management

### 3️⃣ Configure API Credentials

Create a `.env` file in the project root:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
```

**Security Note:** Never commit your `.env` file to version control!

### 4️⃣ Test Connection

```bash
cd src
python client.py
```

Expected output:
```
Testing Binance Futures Testnet connection...
✓ Connection successful!
```

## ▶️ Usage Examples

### Market Orders

Execute immediately at current market price.

```bash
# Buy 0.01 BTC at market price
python src/market_orders.py BTCUSDT BUY 0.01

# Sell 0.005 ETH at market price
python src/market_orders.py ETHUSDT SELL 0.005
```

**Output:**
```
✓ Market order placed successfully!
Order ID: 12345678
Symbol: BTCUSDT
Side: BUY
Quantity: 0.01
Status: FILLED
Average Price: 44523.50
```

### Limit Orders

Execute only when price reaches specified level.

```bash
# Sell 0.01 BTC at 45000 USDT
python src/limit_orders.py BTCUSDT SELL 0.01 45000

# Buy 0.02 ETH at 2500 USDT
python src/limit_orders.py ETHUSDT BUY 0.02 2500
```

**Output:**
```
✓ Limit order placed successfully!
Order ID: 23456789
Symbol: BTCUSDT
Side: SELL
Quantity: 0.01
Price: 45000.00
Status: NEW
```

### Stop-Limit Orders (Advanced)

Triggered at stop price, executed at limit price.

```bash
# Buy 0.01 BTC: trigger at 44000, execute at 44500
python src/advanced/stop_limit.py BTCUSDT BUY 0.01 44000 44500

# Sell 0.01 BTC: trigger at 43000, execute at 42900
python src/advanced/stop_limit.py BTCUSDT SELL 0.01 43000 42900
```

**Price Logic:**
- **BUY**: `stop_price >= limit_price` (buy when price goes up)
- **SELL**: `stop_price <= limit_price` (sell when price goes down)

### OCO Orders (Advanced)

Place both take-profit and stop-loss orders simultaneously.

```bash
# After buying: take profit at 46000, stop loss at 43000/42900
python src/advanced/oco.py BTCUSDT BUY 0.01 46000 43000 42900
```

**Output:**
```
✓ OCO orders placed successfully!

Take Profit Order:
  Order ID: 34567890
  Price: 46000.00
  Status: NEW

Stop Loss Order:
  Order ID: 45678901
  Stop Price: 43000.00
  Limit Price: 42900.00
  Status: NEW
```

### TWAP Strategy (Advanced)

Split large orders into smaller chunks over time.

```bash
# Buy 0.1 BTC split into 10 orders every 30 seconds
python src/advanced/twap.py BTCUSDT BUY 0.1 10 30

# Sell 0.5 ETH split into 20 orders every 60 seconds
python src/advanced/twap.py ETHUSDT SELL 0.5 20 60
```

**Output:**
```
Starting TWAP execution...
Total quantity: 0.1 BTCUSDT
Split into: 10 orders
Interval: 30 seconds

✓ Order 1/10 executed - ID: 56789012
  Waiting 30 seconds...
✓ Order 2/10 executed - ID: 67890123
  Waiting 30 seconds...
...

✓ TWAP execution completed!
Successfully executed: 10/10 orders
Average execution price: 44531.25
```

### Grid Trading Strategy (Advanced)

Create multiple buy/sell orders at predetermined price levels.

```bash
# Create 10 grid levels between 43000 and 47000
python src/advanced/grid_strategy.py BTCUSDT 0.01 43000 47000 10
```

**Output:**
```
Setting up grid strategy for BTCUSDT...
Price range: 43000 - 47000
Grid levels: 10
Quantity per grid: 0.01

✓ Buy order 1 placed at 43000.00
✓ Buy order 2 placed at 43444.44
✓ Buy order 3 placed at 43888.89
✓ Sell order 1 placed at 45111.11
✓ Sell order 2 placed at 45555.56
...

✓ Grid strategy setup completed!
Current market price: 44500.00
Buy orders placed: 3
Sell orders placed: 6
Total orders: 9
```

## 🔍 Input Validation

The bot validates all inputs before making API calls:

| Parameter | Validation Rules |
|-----------|-----------------|
| Symbol | Must be alphanumeric, end with USDT |
| Side | Must be BUY or SELL |
| Quantity | Must be > 0 |
| Price | Must be > 0 |
| Stop Price | Must satisfy relationship with limit price |
| Number of Orders | Must be positive integer |
| Interval | Must be positive integer |

**Example Error:**
```bash
python src/market_orders.py BTCUSDT BUY -0.01
```
```
✗ Validation Error: Quantity must be greater than 0, got: -0.01
```

## 🧾 Logging

All operations are logged to `bot.log` with:
- Timestamp
- Log level (INFO, ERROR, DEBUG)
- Order details
- API responses
- Error tracebacks

**Example Log Entry:**
```
2025-01-09 14:30:45 | INFO     | Order Type: MARKET | Symbol: BTCUSDT | Side: BUY | Quantity: 0.01 | Status: FILLED | Order ID: 12345678
2025-01-09 14:31:12 | ERROR    | Order Type: LIMIT | Symbol: ETHUSDT | Side: SELL | Quantity: 0.02 | Price: 2500.0 | Status: FAILED | Error: APIError(code=-1013): Invalid quantity.
```

## 🛡️ Error Handling

The bot handles various error scenarios:

1. **API Errors**: Invalid credentials, insufficient balance, invalid parameters
2. **Network Errors**: Connection timeouts, DNS failures
3. **Validation Errors**: Invalid input parameters
4. **Runtime Errors**: Unexpected exceptions

All errors are:
- Logged with full tracebacks
- Displayed to user with clear messages
- Handled gracefully without crashes

## 📊 Common Trading Symbols

| Symbol | Description |
|--------|-------------|
| BTCUSDT | Bitcoin / Tether |
| ETHUSDT | Ethereum / Tether |
| BNBUSDT | Binance Coin / Tether |
| ADAUSDT | Cardano / Tether |
| SOLUSDT | Solana / Tether |
| DOGEUSDT | Dogecoin / Tether |

## 🔧 Troubleshooting

### API Connection Fails
```
Error: Missing API credentials
```
**Solution:** Ensure `.env` file exists with valid API keys

### Order Rejected
```
Binance API Error: APIError(code=-1013): Invalid quantity
```
**Solution:** Check symbol's minimum quantity requirements on Binance

### Timestamp Error
```
APIError(code=-1021): Timestamp for this request is outside of the recvWindow
```
**Solution:** Sync your system clock or check network latency

### Insufficient Balance
```
APIError(code=-2019): Margin is insufficient
```
**Solution:** Add more testnet USDT to your account

## 🎓 Learning Resources

- [Binance Futures API Documentation](https://binance-docs.github.io/apidocs/futures/en/)
- [python-binance Library](https://python-binance.readthedocs.io/)
- [Trading Strategy Basics](https://www.binance.com/en/futures/trading-rules)

## 📄 License

This project is for educational purposes. Use at your own risk.

## 🤝 Contributing

Contributions are welcome! Please ensure:
- Code follows existing structure
- All inputs are validated
- Errors are properly handled
- Actions are logged

## ⚠️ Disclaimer

This bot is designed for the Binance USDT-M Futures **Testnet** only. Trading cryptocurrencies involves significant risk. This software is provided "as is" without warranty. Always do your own research before trading with real funds.

---

**Happy Trading! 🚀**

"""
Configuratie Bestand
"""

# 🔄 Exchange Selection
EXCHANGE = 'hyperliquid'  # Options: 'solana', 'hyperliquid'
HYPERLIQUID_TESTNET = True  # Use Hyperliquid testnet for paper trading

# 💰 Trading Configuration
USDC_ADDRESS = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"  # Never trade or close
SOL_ADDRESS = "So11111111111111111111111111111111111111111"   # Never trade or close

# Create a list of addresses to exclude from trading/closing
EXCLUDED_TOKENS = [USDC_ADDRESS, SOL_ADDRESS]

# Token List for Trading 📋
# NOTE: Trading Agent now has its own token list - see src/agents/trading_agent.py lines 101-104
MONITORED_TOKENS = [
    # '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump',    # 🌬️ FART
    # 'DitHyRMQiSDhn5cnKMJV2CDDt6sVct96YrECiM49pump'     # housecoin
]

# Token Trading List
# Zorgvuldig geselecteerde tokens voor trading
tokens_to_trade = MONITORED_TOKENS  # Using the same list for trading

# ⚡ HyperLiquid Configuration
# Top 10 cryptos + Zcash for Volume Profile Mean Reversion Strategy
HYPERLIQUID_SYMBOLS = [
    'BTC',   # Bitcoin
    'ETH',   # Ethereum
    'SOL',   # Solana
    'BNB',   # Binance Coin
    'XRP',   # Ripple
    'ADA',   # Cardano
    'AVAX',  # Avalanche
    'DOGE',  # Dogecoin
    'LINK',  # Chainlink
    'MATIC', # Polygon
    'ZEC'    # Zcash
]

# Leverage Settings (AI decides per trade, max 20x)
HYPERLIQUID_MAX_LEVERAGE = 20  # Maximum leverage allowed (1-50)
HYPERLIQUID_MIN_LEVERAGE = 2   # Minimum leverage for trades

# 🔄 Exchange-Specific Token Lists
# Use this to determine which tokens/symbols to trade based on active exchange
def get_active_tokens():
    """Returns the appropriate token/symbol list based on active exchange"""
    if EXCHANGE == 'hyperliquid':
        return HYPERLIQUID_SYMBOLS
    else:
        return MONITORED_TOKENS

# Token to Exchange Mapping (for future hybrid trading)
TOKEN_EXCHANGE_MAP = {
    'BTC': 'hyperliquid',
    'ETH': 'hyperliquid',
    'SOL': 'hyperliquid',
    # All other tokens default to Solana
}

# Token and wallet settings
symbol = '9BB6NFEcjBCtnNLFko2FqVQBq8HHM13kCyYcdQbgpump'
address = '4wgfCBf2WwLSRKLef9iW7JXZ2AfkxUxGM4XcKpHm3Sin' # YOUR WALLET ADDRESS HERE

# Position sizing 🎯
TESTNET_CAPITAL = 1000  # Total testnet capital in USD
usd_size = 50  # Default position size per trade
max_usd_order_size = 100  # Max order size per trade
tx_sleep = 5  # Sleep between transactions (reduced for testnet)
slippage = 199  # Slippage settings

# Risk Management Settings 🛡️ (Optimized for scalping)
CASH_PERCENTAGE = 30  # Minimum % to keep in USDC as safety buffer (0-100)
MAX_POSITION_PERCENTAGE = 10  # Maximum % allocation per position (scalping = smaller positions)
STOPLOSS_PRICE = 1 # NOT USED YET 1/5/25    
BREAKOUT_PRICE = .0001 # NOT USED YET 1/5/25
SLEEP_AFTER_CLOSE = 600  # Prevent overtrading

MAX_LOSS_GAIN_CHECK_HOURS = 12  # How far back to check for max loss/gain limits (in hours)
SLEEP_BETWEEN_RUNS_MINUTES = 15  # How long to sleep between agent runs 🕒


# Max Loss/Gain Settings FOR RISK AGENT 1/5/25
USE_PERCENTAGE = False  # If True, use percentage-based limits. If False, use USD-based limits

# USD-based limits (used if USE_PERCENTAGE is False)
MAX_LOSS_USD = 25  # Maximum loss in USD before stopping trading
MAX_GAIN_USD = 25 # Maximum gain in USD before stopping trading

# USD MINIMUM BALANCE RISK CONTROL
MINIMUM_BALANCE_USD = 50  # If balance falls below this, risk agent will consider closing all positions
USE_AI_CONFIRMATION = True  # If True, consult AI before closing positions. If False, close immediately on breach

# Percentage-based limits (used if USE_PERCENTAGE is True)
MAX_LOSS_PERCENT = 5  # Maximum loss as percentage (e.g., 20 = 20% loss)
MAX_GAIN_PERCENT = 5  # Maximum gain as percentage (e.g., 50 = 50% gain)

# Transaction settings ⚡
slippage = 199  # 500 = 5% and 50 = .5% slippage
PRIORITY_FEE = 100000  # ~0.02 USD at current SOL prices
orders_per_open = 3  # Multiple orders for better fill rates

# Market maker settings 📊
buy_under = .0946
sell_over = 1

# Data collection settings 📈
DAYSBACK_4_DATA = 3
DATA_TIMEFRAME = '1H'  # 1m, 3m, 5m, 15m, 30m, 1H, 2H, 4H, 6H, 8H, 12H, 1D, 3D, 1W, 1M
SAVE_OHLCV_DATA = False  # Zet op True om data permanent op te slaan, False gebruikt alleen tijdelijke data

# AI Model Settings 🤖
AI_MODEL_TYPE = "deepseek"  # Use DeepSeek for trade analysis and confirmation
AI_MODEL = "deepseek-reasoner"  # DeepSeek's reasoning model
AI_MAX_TOKENS = 2048  # Max tokens for response (increased for reasoning)
AI_TEMPERATURE = 0.3  # Lower temperature for more precise analysis (0-1)
AI_CONFIRMATION_REQUIRED = True  # Require AI confirmation for every trade

# Volume Profile Mean Reversion Strategy Settings 📊
ENABLE_STRATEGIES = True  # Enable strategy-based trading
STRATEGY_TYPE = 'volume_profile'  # Active strategy
STRATEGY_TIMEFRAMES = ['1m', '5m']  # Run strategy on both timeframes
STRATEGY_MIN_CONFIDENCE = 70  # Minimum development score to trade (0-100)

# Volume Profile Strategy Parameters
VP_LOOKBACK_MIN = 50  # Minimum candles for volume profile
VP_LOOKBACK_MAX = 120  # Maximum candles for volume profile
VP_TP_FRACTION = 0.9  # Take profit at 90% distance to POC
VP_ATR_MIN = 0.15  # Minimum ATR % for valid setup
VP_ATR_MAX = 0.55  # Maximum ATR % for valid setup
VP_TIMEOUT_CANDLES = 15  # Max candles to hold position

# Sleep time between main agent runs
SLEEP_BETWEEN_RUNS_MINUTES = 15  # How long to sleep between agent runs 🕒

# in our nice_funcs in token over view we look for minimum trades last hour
MIN_TRADES_LAST_HOUR = 2


# Real-Time Clips Agent Settings 🎬
REALTIME_CLIPS_ENABLED = True
REALTIME_CLIPS_OBS_FOLDER = '/Volumes/Moon 26/OBS'  # Your OBS recording folder
REALTIME_CLIPS_AUTO_INTERVAL = 120  # Check every N seconds (120 = 2 minutes)
REALTIME_CLIPS_LENGTH = 2  # Minutes to analyze per check
REALTIME_CLIPS_AI_MODEL = 'groq'  # Model type: groq, openai, claude, deepseek, xai, ollama
REALTIME_CLIPS_AI_MODEL_NAME = None  # None = use default for model type
REALTIME_CLIPS_TWITTER = True  # Auto-open Twitter compose after clip

# Future variables (not active yet) 🔮
sell_at_multiple = 3
USDC_SIZE = 1
limit = 49
timeframe = '15m'
stop_loss_perctentage = -.24
EXIT_ALL_POSITIONS = False
DO_NOT_TRADE_LIST = ['777']
CLOSED_POSITIONS_TXT = '777'
minimum_trades_in_last_hour = 777

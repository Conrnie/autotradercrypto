# 🌙 Moon Dev AI Trading System - Quick Start Guide

## 🎉 System Built Successfully!

Your Volume Profile Mean Reversion AI Trading System is ready to run!

---

## 📋 System Overview

### Core Components

**4 Active Agents:**
1. **Risk Agent** - Monitors portfolio health, enforces position limits and PnL thresholds
2. **Liquidation Agent** - Tracks market liquidation events for context
3. **Strategy Agent** - Scans 11 symbols × 2 timeframes = 22 markets for Volume Profile signals
4. **Trading Agent** - DeepSeek AI analyzes and confirms every trade

### Strategy: Volume Profile Mean Reversion Scalper

**Objective:** Scalp mean reversion toward POC from statistical extremes

**Entry Conditions:**
- Developed volume profile (50-120 candle lookback)
- Price touches ±1σ or ±2σ
- Next candle closes back inside value area
- ATR between 0.15%-0.55%

**Exit Conditions:**
- Take profit: 0.9× distance to POC
- Stop loss: Beyond ±2σ with buffer
- Timeout: 15 candles

---

## 🚀 Getting Started

### Step 1: Environment Setup

Make sure you have your `.env` file configured:

```bash
# Required for AI Trading
DEEPSEEK_KEY=your_deepseek_api_key_here

# Required for Hyperliquid (Testnet)
HYPER_LIQUID_KEY=your_hyperliquid_private_key_here

# Optional (for liquidation data)
MOONDEV_API_KEY=your_moondev_api_key_here
```

### Step 2: Activate Conda Environment

```bash
conda activate tflow
```

### Step 3: Install/Update Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Run the System

```bash
cd src
python main.py
```

---

## 📊 What to Expect

### Startup Sequence

1. **System Banner** - Shows configuration (symbols, timeframes, capital, leverage)
2. **Agent Initialization** - All 4 agents load and initialize
3. **Trading Loop Begins** - System enters continuous scanning mode

### Trading Cycle (Every 15 minutes by default)

```
🔄 CYCLE #1
├─ 🛡️  STEP 1: Risk Management Check
│  └─ Verifies portfolio health, checks limits
│
├─ 📊 STEP 2: Liquidation Context Analysis
│  └─ Gathers market liquidation data
│
├─ 🎯 STEP 3: Volume Profile Signal Generation
│  ├─ Scans BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOGE, LINK, MATIC, ZEC
│  ├─ Checks both 1m and 5m timeframes
│  └─ Generates signals for developed volume profiles
│
└─ 🤖 STEP 4: DeepSeek AI Confirmation & Execution
   ├─ Each signal sent to DeepSeek for analysis
   ├─ AI approves or rejects based on quality
   ├─ AI can adjust leverage and position size
   └─ Approved trades are executed (paper mode)
```

---

## ⚙️ Configuration

All settings are in `src/config.py`:

### Trading Parameters

```python
# Capital
TESTNET_CAPITAL = 1000  # $1000 mock capital

# Symbols (Top 10 + Zcash)
HYPERLIQUID_SYMBOLS = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'ADA',
                       'AVAX', 'DOGE', 'LINK', 'MATIC', 'ZEC']

# Timeframes
STRATEGY_TIMEFRAMES = ['1m', '5m']

# Leverage
HYPERLIQUID_MAX_LEVERAGE = 20  # AI decides per trade (2x-20x)
HYPERLIQUID_MIN_LEVERAGE = 2

# Position Sizing
usd_size = 50  # Default position size
MAX_POSITION_PERCENTAGE = 10  # Max 10% per position (scalping)
CASH_PERCENTAGE = 30  # Keep 30% cash reserve
```

### Volume Profile Strategy Parameters

```python
VP_LOOKBACK_MIN = 50       # Minimum candles for profile
VP_LOOKBACK_MAX = 120      # Maximum candles for profile
VP_TP_FRACTION = 0.9       # Take profit at 90% to POC
VP_ATR_MIN = 0.15          # Minimum ATR %
VP_ATR_MAX = 0.55          # Maximum ATR %
VP_TIMEOUT_CANDLES = 15    # Max hold time
```

### AI Settings

```python
AI_MODEL_TYPE = "deepseek"
AI_MODEL = "deepseek-reasoner"
AI_TEMPERATURE = 0.3       # Lower = more precise
AI_MAX_TOKENS = 2048
AI_CONFIRMATION_REQUIRED = True  # Every trade needs AI approval
```

### Risk Management

```python
MAX_LOSS_USD = 25          # Max loss before stopping
MAX_GAIN_USD = 25          # Max gain before reviewing
MINIMUM_BALANCE_USD = 50   # Minimum balance threshold
```

---

## 🧪 Testing Individual Components

### Test Volume Profile Strategy

```bash
cd src/strategies
python volume_profile_strategy.py
```

This will:
- Fetch BTC 1m data
- Calculate volume profile
- Check if profile is "developed"
- Generate a signal if conditions are met

### Test Strategy Agent

```bash
cd src/agents
python strategy_agent.py
```

This will:
- Initialize all 22 strategies (11 symbols × 2 timeframes)
- Scan all markets
- Display any signals found

### Test Trading Agent (DeepSeek Confirmation)

```bash
cd src/agents
python trading_agent.py
```

This will:
- Load DeepSeek AI model
- Test with a sample signal
- Show AI's approval/rejection reasoning

---

## 📈 Understanding the Output

### Volume Profile Analysis

```
🔍 Analyzing BTC on 1m timeframe
✅ Fetched 200 candles
📊 ATR: 0.350%
✅ Found developed profile (Score: 85.5, Lookback: 80)
   POC: $45100.00
   Value Area: $44900.00 - $45300.00
   ±2σ Range: $44700.00 - $45500.00
📈 Current Price: $44850.00

🟢 LONG SETUP DETECTED!
   Entry Level: 2σ
   Entry: $44850.00
   Target: $45080.00
   Stop: $44675.00
   R:R: 2.5
   Leverage: 8x
```

### DeepSeek AI Analysis

```
🤖 DEEPSEEK AI TRADE ANALYSIS
📤 Sending signal to DeepSeek for analysis...

📥 DeepSeek Response:
APPROVE

This is a high-quality mean reversion setup:

1. Volume Profile Quality (Score: 85.5) - Excellent development
2. Entry at -2σ is ideal for mean reversion
3. R:R of 2.5:1 is favorable
4. ATR at 0.35% is in optimal range
5. Leverage of 8x is reasonable given the tight stop

ADJUST_LEVERAGE: 6x (slightly conservative given testnet)

✅ TRADE APPROVED BY DEEPSEEK
⚙️ DeepSeek adjusted leverage: 8x → 6x
```

---

## 🛡️ Safety Features

### Built-in Protections

1. **Testnet Mode** - Currently configured for Hyperliquid testnet (no real money)
2. **AI Confirmation** - Every trade must be approved by DeepSeek
3. **Risk Limits** - Max loss/gain thresholds enforced
4. **Position Limits** - Max 10% per position
5. **Timeout Protection** - Positions auto-close after 15 candles
6. **Cash Reserve** - Always keeps 30% in cash

### Emergency Stops

- Risk Agent will halt trading if:
  - Balance falls below minimum
  - Max loss threshold reached
  - Max gain threshold reached (forces review)

---

## 📝 Trade Logging

All trades are logged to: `src/data/trade_log.jsonl`

Each entry includes:
- Timestamp
- Symbol and direction
- Entry/target/stop prices
- Leverage and position size
- Volume profile data
- Strategy reasoning
- DeepSeek AI reasoning

---

## 🔧 Troubleshooting

### "DEEPSEEK_KEY not found"
Add your DeepSeek API key to `.env` file

### "HYPER_LIQUID_KEY not found"
Add your Hyperliquid private key to `.env` file (testnet wallet)

### "No data returned by API"
- Check internet connection
- Verify Hyperliquid testnet API is accessible
- Try a different symbol

### "No signals generated"
This is normal! Volume profiles are picky:
- Profile must be "developed" (quality score >70)
- Price must touch extremes and revert
- ATR must be in range
- Most cycles won't have signals

### "DeepSeek rejects all trades"
Also normal! DeepSeek is very critical:
- Low R:R ratio
- Poor volume profile quality
- High leverage risk
- Unfavorable market context

---

## 📊 Performance Tracking

Monitor your system:

1. **Console Output** - Real-time cycle summaries
2. **Trade Log** - `src/data/trade_log.jsonl`
3. **Agent Data** - `src/data/*` directories

---

## 🎯 Next Steps

### 1. Verify Testnet Setup

Make sure you're actually on Hyperliquid testnet:
- Check `config.py`: `HYPERLIQUID_TESTNET = True`
- Verify your testnet wallet has funds

### 2. Customize Settings

Tune the strategy to your preferences:
- Adjust timeframes
- Change symbols
- Modify risk limits
- Tweak volume profile parameters

### 3. Monitor Performance

Let the system run for 24 hours and review:
- How many signals were generated?
- How many were approved by DeepSeek?
- What was the approval rate?
- Are the setups logical?

### 4. Integrate Live Trading (When Ready)

Once you're confident with paper trading:
1. **DO NOT** rush to live trading
2. Test thoroughly on testnet first
3. Start with minimal capital
4. Gradually increase size

---

## 🆘 Support

### Documentation

- `CLAUDE.md` - Project overview and development guide
- `docs/` - Agent-specific documentation
- `README.md` - Original project README

### Community

- Moon Dev Discord: Join the community
- GitHub Issues: Report bugs or ask questions

---

## ⚠️ Important Reminders

1. **This is experimental software** - Use at your own risk
2. **Paper trade first** - Test thoroughly before using real money
3. **Never invest more than you can afford to lose**
4. **Past performance does not guarantee future results**
5. **AI decisions are not financial advice**
6. **Always monitor your positions**
7. **Keep your API keys secure**

---

## 🌙 Happy Trading!

Your AI trading system is ready to scan markets 24/7!

To start:
```bash
conda activate tflow
cd src
python main.py
```

Let the AI find the opportunities! 🚀

# 🤖 AI Cryptocurrency Trading Systeem

Een geavanceerd, AI-gestuurd trading systeem voor cryptocurrency markten, gebouwd met DeepSeek AI en Volume Profile analyse.

## 📋 Inhoudsopgave

- [Overzicht](#overzicht)
- [Kenmerken](#kenmerken)
- [Architectuur](#architectuur)
- [Installatie](#installatie)
- [Configuratie](#configuratie)
- [Gebruik](#gebruik)
- [Trading Strategie](#trading-strategie)
- [Database Schema](#database-schema)
- [API Documentatie](#api-documentatie)
- [Troubleshooting](#troubleshooting)

## 🎯 Overzicht

Dit project demonstreert een volledig functioneel AI-gestuurd trading systeem dat:

- **DeepSeek AI** gebruikt voor alle trading beslissingen
- **Volume Profile Mean Reversion** strategie implementeert
- Handelt op **Hyperliquid testnet** (paper trading)
- **Alle trades analyseert** voordat ze worden uitgevoerd
- **Complete audit trail** bijhoudt in SQLite database
- **Risicobeheer** met circuit breakers

### 💡 Educatief Doel

Dit is een **portfolio project** om te demonstreren:
- Multi-agent AI architectuur
- Kwantitatieve trading strategieën
- Real-time marktdata analyse
- Database design voor trading systemen
- API integratie (DeepSeek, Hyperliquid)
- Python best practices

⚠️ **Waarschuwing**: Dit is voor educatieve doeleinden. Gebruik nooit echt geld zonder grondig begrip van de risico's.

## ✨ Kenmerken

### Trading Functionaliteit
- ✅ **11 Cryptocurrency Paren**: BTC, ETH, SOL, BNB, XRP, ADA, AVAX, DOGE, LINK, MATIC, ZEC
- ✅ **Multi-Timeframe Analyse**: 1 minuut en 5 minuten grafieken
- ✅ **AI Bevestiging**: DeepSeek analyseert elk signaal voordat executie
- ✅ **Dynamische Leverage**: 2x-20x, beslist door AI
- ✅ **Testnet Paper Trading**: $1000 virtueel kapitaal

### Risk Management
- 🛡️ **Portfolio Limieten**: Maximaal verlies/winst per dag
- 🛡️ **Positie Monitoring**: Real-time tracking van open posities
- 🛡️ **Stop Loss & Take Profit**: Automatische exit condities
- 🛡️ **Timeout Mechanisme**: Sluit posities na X candles

### Data & Logging
- 📊 **SQLite Database**: Alle trades en beslissingen opgeslagen
- 📊 **Market Data**: OHLCV data van Hyperliquid
- 📊 **AI Beslissingen**: Prompt, response en redenering gelogd
- 📊 **Performance Metrics**: PnL tracking en statistieken

## 🏗️ Architectuur

### Agent-Based Systeem

Het systeem bestaat uit 4 gespecialiseerde agents:

```
┌─────────────────────────────────────────────────────────────┐
│                     MAIN TRADING CYCLE                      │
│                    (Elke 15 minuten)                        │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────────┐
        │    1. RISK AGENT                            │
        │    - Check portfolio waarde ($1000)         │
        │    - Verifieer limieten                     │
        │    - Circuit breaker controle               │
        └─────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────────┐
        │    2. POSITION MANAGER                      │
        │    - Monitor open posities                  │
        │    - Check TP/SL/Timeout                    │
        │    - Vraag AI voor exit bevestiging        │
        └─────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────────┐
        │    3. LIQUIDATION AGENT                     │
        │    - Analyseer liquidatie data              │
        │    - Detecteer spikes in liquidaties        │
        │    - Verzamel markt context                 │
        └─────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────────┐
        │    4. STRATEGY AGENT                        │
        │    - Scan 22 strategieën                    │
        │    - Genereer Volume Profile signalen       │
        │    - Filter op ATR volatiliteit             │
        └─────────────────────────────────────────────┘
                              │
                              ▼
        ┌─────────────────────────────────────────────┐
        │    5. TRADING AGENT                         │
        │    - Stuur signaal naar DeepSeek AI         │
        │    - Analyseer risk/reward ratio            │
        │    - Goedkeuren of afwijzen                 │
        │    - Executeer op Hyperliquid (indien OK)   │
        └─────────────────────────────────────────────┘
```

### Volume Profile Strategie

**Mean Reversion** op basis van Volume Profile:

1. **Profile Berekening**
   - 50-120 candle lookback periode
   - Point of Control (POC): Hoogste volume prijs
   - Value Area: ±1σ en ±2σ grenzen
   - Statistieke validatie (drift, skewness, kurtosis)

2. **Entry Condities**
   - **LONG**: Prijs raakt ondergrens (±1σ/±2σ) → candle sluit binnen value area
   - **SHORT**: Prijs raakt bovengrens (±1σ/±2σ) → candle sluit binnen value area
   - ATR tussen 0.15%-0.55% (volatiliteit filter)

3. **Exit Condities**
   - **Take Profit**: 0.9× afstand tot POC
   - **Stop Loss**: Buiten value area
   - **Timeout**: 15 candles zonder beweging

### DeepSeek AI Analyse

Voor **elk** trading signaal analyseert DeepSeek:

```python
✅ Volume Profile kwaliteit (score > 75%)
✅ Risk/Reward ratio (minimum 2:1)
✅ ATR volatiliteit (optimaal bereik)
✅ Entry niveau (±1σ of ±2σ)
✅ Markt context (liquidatie data)
✅ Leverage geschiktheid (2x-20x)
```

**Voorbeeld AI Beslissing:**

```
REJECT

De risk/reward ratio van 0.11 is kritisch slecht, ver onder het minimaal vereiste
2:1. Met entry op $192.58, target op $192.44 en stop loss op $193.85, is het
risico ($1.27) aanzienlijk groter dan de reward ($0.14). Dit maakt de trade
niet winstgevend op lange termijn.
```

## 🚀 Installatie

### Vereisten

- Python 3.11+
- pip
- Git

### Stap 1: Clone Repository

```bash
git clone https://github.com/jouw-username/autotradeclone.git
cd autotradeclone
```

### Stap 2: Installeer Dependencies

```bash
pip install -r requirements.txt
```

### Stap 3: Configureer Environment

Kopieer `.env_example` naar `.env`:

```bash
cp .env_example .env
```

Bewerk `.env` en voeg je API keys toe:

```bash
# Vereist voor AI trading
DEEPSEEK_KEY=sk-jouw-deepseek-api-key

# Vereist voor Hyperliquid testnet
HYPER_LIQUID_KEY=jouw-ethereum-private-key

# Optioneel (niet nodig voor Hyperliquid)
MOONDEV_API_KEY=jouw-api-key
```

### Stap 4: Verifieer Setup

```bash
python verify_env.py
```

## ⚙️ Configuratie

### Primaire Configuratie: `src/config.py`

```python
# Exchange Instellingen
EXCHANGE = 'hyperliquid'          # Trading platform
HYPERLIQUID_TESTNET = True        # Gebruik testnet (paper trading)
TESTNET_CAPITAL = 1000            # Virtueel kapitaal ($)

# Trading Paren
HYPERLIQUID_SYMBOLS = [
    'BTC', 'ETH', 'SOL', 'BNB', 'XRP',
    'ADA', 'AVAX', 'DOGE', 'LINK', 'MATIC', 'ZEC'
]

# Timeframes
STRATEGY_TIMEFRAMES = ['1m', '5m']

# Risk Management
MAX_LOSS_USD = 200                # Stop trading bij -$200 verlies
MAX_GAIN_USD = 500                # Stop trading bij +$500 winst
MINIMUM_BALANCE_USD = 50          # Minimum portfolio waarde

# AI Instellingen
AI_MODEL_TYPE = "deepseek"
AI_MODEL = "deepseek-reasoner"
AI_TEMPERATURE = 0.3
AI_MAX_TOKENS = 2048

# Timing
SLEEP_BETWEEN_RUNS_MINUTES = 15  # Scan elke 15 minuten
```

## 🎮 Gebruik

### Start Trading Systeem

```bash
cd src
python main.py
```

### Verwachte Output

```
====================================================================================================
                                 🤖 AI TRADING SYSTEEM
====================================================================================================

📊 STRATEGIE: Volume Profile Mean Reversion Scalper
🤖 AI MODEL: DeepSeek Reasoner (Bevestiging Vereist)
💱 EXCHANGE: Hyperliquid Testnet (Paper Trading)
📈 SYMBOLEN: 11 crypto paren
⏱️  TIMEFRAMES: 1m, 5m
💰 KAPITAAL: $1000 USD (Mock)
📊 LEVERAGE: 2x - 20x (AI Beslist)
====================================================================================================

🔧 Initialiseren agents...
✅ Alle agents succesvol geïnitialiseerd!

🔄 TRADING CYCLUS #1
⏰ 2025-10-23 16:09:23

🛡️  STAP 1: RISICOBEHEER CONTROLE
✅ Alle risico limieten OK

👁️  STAP 2: POSITIE MONITORING
⚪ Geen open posities

📊 STAP 3: LIQUIDATIE ANALYSE
✨ Liquidatie context verzameld

🎯 STAP 4: SIGNAAL GENERATIE
📊 Scanning BTC...
   ⚪ Geen entry condities voldaan

📊 SCAN SAMENVATTING
   Totaal signalen: 0

😴 Slapen tot volgende run (15 minuten)
```

### Database Queries

Bekijk AI beslissingen:

```bash
sqlite3 src/data/trading.db

# Alle AI beslissingen
SELECT * FROM ai_decisions ORDER BY timestamp DESC LIMIT 10;

# Open trades
SELECT * FROM trades WHERE status = 'open';

# Performance overzicht
SELECT * FROM performance_log ORDER BY timestamp DESC LIMIT 10;
```

## 📊 Trading Strategie Details

### Volume Profile Mean Reversion

**Concept**: Prijzen keren terug naar het gemiddelde (POC) wanneer ze te ver van het centrum afwijken.

**Technische Indicators**:
- **POC (Point of Control)**: Prijs met hoogste volume
- **Value Area**: ±1σ (68% van volume)
- **Extreme Area**: ±2σ (95% van volume)
- **ATR**: Volatiliteit meting

**Entry Setup LONG**:

```
Prijs ──┐
        │
        │          ┌──── +2σ: $193.49
        │          │
        │          ├──── +1σ: $192.71 (SHORT entry zone)
        │          │
        │ ┌────────┼──── POC: $192.34 (Target)
        │ │        │
        │ │        ├──── -1σ: $191.15 (LONG entry zone) ← ENTRY HIER
        │ │        │
        └─┼────────┴──── -2σ: $190.38
          │
          └─ Mean reversion naar POC
```

**Trade Parameters**:

| Parameter | Waarde | Reden |
|-----------|--------|-------|
| Entry | ±1σ of ±2σ | Extreem van value area |
| Target | 0.9× afstand POC | Conservatieve mean reversion |
| Stop Loss | Buiten ±2σ | Profile is gebroken |
| Timeout | 15 candles | Geen momentum |
| Leverage | 2x-20x | AI beslist op basis van confidence |

**Risk/Reward Vereisten**:

DeepSeek **wijst af** als:
- R:R ratio < 2:1
- Volume profile score < 75%
- ATR buiten 0.15%-0.55%
- Geen duidelijke entry setup

## 🗄️ Database Schema

### Tabellen

**1. ai_decisions**
```sql
- id (PRIMARY KEY)
- prompt (TEXT)                  -- Volledige prompt naar AI
- response (TEXT)                -- AI antwoord
- market_snapshot (JSON)         -- Marktdata op moment van beslissing
- capital_at_decision (REAL)     -- Portfolio waarde
- model_used (TEXT)              -- "deepseek-reasoner"
- timestamp (TEXT)
```

**2. trades**
```sql
- id (PRIMARY KEY)
- decision_id (FOREIGN KEY)      -- Link naar AI beslissing
- symbol (TEXT)                  -- "BTC", "ETH", etc.
- action (TEXT)                  -- "LONG" of "SHORT"
- size (REAL)                    -- Positie grootte in USD
- leverage (REAL)                -- 2-20x
- entry_price (REAL)
- stop_loss (REAL)
- take_profit (REAL)
- strategy (TEXT)                -- "volume_profile"
- confidence (REAL)              -- 0-100%
- status (TEXT)                  -- "open", "closed", "cancelled"
- pnl (REAL)                     -- Profit/Loss
- exit_price (REAL)
- exit_reason (TEXT)             -- "tp", "sl", "timeout", "manual"
- timestamp (TEXT)
```

**3. position_updates**
```sql
- id (PRIMARY KEY)
- trade_id (FOREIGN KEY)
- current_price (REAL)
- unrealized_pnl (REAL)
- action_taken (TEXT)            -- "hold", "close", "adjust_sl"
- reason (TEXT)
- timestamp (TEXT)
```

**4. performance_log**
```sql
- id (PRIMARY KEY)
- portfolio_value (REAL)
- total_pnl (REAL)
- open_positions (INTEGER)
- trades_today (INTEGER)
- win_rate (REAL)
- timestamp (TEXT)
```

## 🔌 API Documentatie

### DeepSeek AI API

**Endpoint**: `https://api.deepseek.com`

**Model**: `deepseek-reasoner`

**Usage**:
```python
from src.models.model_factory import model_factory

model = model_factory.get_model("deepseek")
response = model.generate_response(
    system_prompt="Je bent een trading analist.",
    user_content="Analyseer dit signaal: ...",
    temperature=0.3,
    max_tokens=2048
)
```

### Hyperliquid Testnet API

**Endpoint**: `https://api.hyperliquid-testnet.xyz/info`

**Functies**:
```python
from src.hyperliquid_executor import HyperliquidExecutor

executor = HyperliquidExecutor()

# Get account waarde
balance = executor.get_account_value()

# Market order
result = executor.market_order(
    symbol="BTC",
    is_buy=True,
    size_usd=100,
    leverage=5
)

# Sluit positie
executor.close_position(symbol="BTC")
```

## 🛠️ Troubleshooting

### Veelvoorkomende Problemen

**1. HTTP 429 Rate Limiting**
```
Oplossing: Systeem heeft automatisch exponential backoff.
Wacht 2-6 seconden tussen requests.
```

**2. Geen Signalen Gegenereerd**
```
Reden: Volume Profile vereist specifieke condities:
- Prijs bij ±1σ of ±2σ grenzen
- ATR tussen 0.15%-0.55%
- Ontwikkeld profile (score > 75%)

Dit is normaal. Meeste cycli genereren 0 signalen.
```

**3. DeepSeek Wijst Alles Af**
```
Dit is GOED! DeepSeek beschermt je kapitaal.
Check de redenen in de logs:
- R:R ratio < 2:1
- Lage confidence
- Slechte markt condities
```

**4. Database Errors**
```bash
# Reset database
rm src/data/trading.db
python src/main.py  # Creëert nieuwe database
```

## 📝 Licentie

Dit project is voor educatieve doeleinden. Gebruik op eigen risico.

---

**Disclaimer**: Dit is een demonstratie project voor portfolio doeleinden. Nooit gebruiken met echt geld zonder grondig begrip van algoritmische trading risico's.

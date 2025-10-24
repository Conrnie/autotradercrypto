# CLAUDE.md

Dit bestand biedt richtlijnen voor Claude Code (claude.ai/code) bij het werken met code in deze repository.

## Project Overzicht

Dit is een AI trading systeem dat gespecialiseerde AI agents gebruikt om markten te analyseren, strategieën uit te voeren en risico's te beheren voor cryptocurrency markten op Hyperliquid. Het project gebruikt een modulaire agent architectuur met DeepSeek AI voor alle trading beslissingen.

## Belangrijke Commando's

### Environment Setup
```bash
# Install/update dependencies
pip install -r requirements.txt

# Update requirements.txt when adding packages
pip freeze > requirements.txt
```

### Systeem Draaien
```bash
# Run main orchestrator
python src/main.py

# Run individual agents standalone
python src/agents/risk_agent.py
python src/agents/strategy_agent.py
python src/agents/liquidation_agent.py
python src/agents/trading_agent.py
```

## Architectuur Overzicht

### Core Structuur
```
src/
├── agents/              # 4 gespecialiseerde AI agents
│   ├── risk_agent.py           # Risicobeheer met circuit breakers
│   ├── strategy_agent.py       # Volume Profile strategie
│   ├── liquidation_agent.py    # Liquidatie data analyse
│   ├── trading_agent.py        # DeepSeek AI trade bevestiging
│   └── position_manager.py     # Open posities monitoren
├── models/              # DeepSeek AI integratie
│   ├── model_factory.py        # ModelFactory voor DeepSeek
│   ├── base_model.py           # Base model interface
│   └── deepseek_model.py       # DeepSeek implementatie
├── strategies/          # Trading strategieën
│   └── volume_profile_strategy.py  # Volume Profile Mean Reversion
├── data/                # Database en outputs
│   └── trading.db              # SQLite database met audit trail
├── config.py            # Globale configuratie
├── main.py              # Main orchestrator loop
├── database.py          # Database interface
├── hyperliquid_executor.py  # Hyperliquid API interface
├── nice_funcs.py        # Shared trading utilities (Solana - optioneel)
└── nice_funcs_hl.py     # Hyperliquid-specific utilities
```

### Agent Ecosystem

**4 Core Agents**:
1. **Risk Agent** (`risk_agent.py`): Portfolio risk management
   - Controleert portfolio waarde
   - Enforced max loss/gain limieten
   - Circuit breaker functionaliteit

2. **Strategy Agent** (`strategy_agent.py`): Volume Profile signaal generatie
   - Scant 11 symbolen × 2 timeframes = 22 strategieën
   - Volume Profile Mean Reversion detectie
   - ATR volatiliteit filtering

3. **Liquidation Agent** (`liquidation_agent.py`): Markt context
   - Monitort liquidatie spikes
   - Verzamelt markt sentiment
   - Gebruikt DeepSeek voor analyse

4. **Trading Agent** (`trading_agent.py`): AI bevestiging & executie
   - DeepSeek analyseert elk signaal
   - Risk/reward validatie (min 2:1)
   - Executie op Hyperliquid testnet

**Position Manager** (`position_manager.py`): Open posities
   - Monitort TP/SL/Timeout
   - DeepSeek bevestigt exits
   - Update database

### AI Integration (DeepSeek Only)

**Unified Interface**: Alle agents gebruiken `model_factory.get_model("deepseek")`

**Key Pattern**:
```python
from src.models.model_factory import model_factory

model = model_factory.get_model("deepseek")
response = model.generate_response(
    system_prompt="Je bent een trading analist.",
    user_content=prompt_text,
    temperature=0.3,
    max_tokens=2048
)
```

### Configuratie Management

**Primaire Config**: `src/config.py`
- Exchange: `EXCHANGE = 'hyperliquid'`, `HYPERLIQUID_TESTNET = True`
- Symbolen: `HYPERLIQUID_SYMBOLS = ['BTC', 'ETH', 'SOL', ...]`
- Timeframes: `STRATEGY_TIMEFRAMES = ['1m', '5m']`
- Risk: `MAX_LOSS_USD`, `MAX_GAIN_USD`, `MINIMUM_BALANCE_USD`
- AI: `AI_MODEL_TYPE = "deepseek"`, `AI_MODEL = "deepseek-reasoner"`
- Timing: `SLEEP_BETWEEN_RUNS_MINUTES = 15`

**Environment Variables**: `.env`
- AI: `DEEPSEEK_KEY` (vereist)
- Trading: `HYPER_LIQUID_KEY` (vereist voor testnet)
- Optioneel: `MOONDEV_API_KEY` (voor liquidatie data)

### Shared Utilities

**`src/nice_funcs_hl.py`**: Hyperliquid functies
- `get_data()`: OHLCV data ophalen
- `adjust_timestamp()`: Timestamp correctie
- ATR en indicator berekeningen

**`src/database.py`**: SQLite database interface
- `log_ai_decision()`: AI beslissingen opslaan
- `log_trade()`: Trade execution logging
- `get_open_positions()`: Query open posities
- `update_trade()`: Update trade status

**`src/hyperliquid_executor.py`**: Trading executie
- `market_order()`: Execute market orders
- `close_position()`: Sluit posities
- `get_account_value()`: Portfolio waarde
- Testnet mode support

### Data Flow Pattern

```
Config → Agent Init → Market Data (Hyperliquid) → Data Parsing →
DeepSeek AI Analysis → Decision Output →
Database Logging (SQLite) → Trade Execution (if approved)
```

## Development Rules

### File Management
- **Keep agents under 800 lines** - if longer, split into new files
- **Update requirements.txt** after adding any new package
- **Never expose API keys** in code or logs

### Code Style
- **Real data only** - no synthetic/fake data
- **Minimal error handling** - let errors surface for debugging
- **Clear logging** - use termcolor for important messages
- **Type hints** where helpful

### Agent Development Pattern

Agents volgen dit patroon:
1. Import `model_factory` voor DeepSeek AI
2. Initialize database connectie indien nodig
3. Implement `run()` method voor main cycle
4. Implement `run_standalone()` voor independent execution
5. Log outputs naar `src/data/[agent_name]/`

Voorbeeld:
```python
from src.models.model_factory import model_factory
from src.database import TradingDatabase

class NewAgent:
    def __init__(self):
        self.model = model_factory.get_model("deepseek")
        self.db = TradingDatabase()

    def run(self):
        # Main agent logic voor cycle
        pass

    def run_standalone(self):
        # Standalone execution met loop
        while True:
            self.run()
            time.sleep(600)

if __name__ == "__main__":
    agent = NewAgent()
    agent.run_standalone()
```

### Trading Strategy Pattern

Strategieën in `src/strategies/`:
```python
class VolumeProfileStrategy:
    def __init__(self, symbol, timeframe):
        self.symbol = symbol
        self.timeframe = timeframe

    def generate_signals(self) -> Dict:
        # Fetch data
        data = get_data(self.symbol, self.timeframe)

        # Calculate indicators
        profile = self.calculate_volume_profile(data)

        # Check entry conditions
        signal = self.check_entry_conditions(profile, data)

        return {
            "symbol": self.symbol,
            "direction": "LONG"|"SHORT"|"NEUTRAL",
            "confidence": 0-100,
            "leverage": 2-20,
            "entry_price": float,
            "stop_loss": float,
            "take_profit": float,
            "reasoning": "explanation"
        }
```

## Important Context

### Risk-First Philosophy
- Risk Agent draait **eerst** in main loop
- Configurable circuit breakers stoppen trading bij limieten
- DeepSeek AI bevestigt **alle** trades voordat executie
- Testnet only - geen echt geld

### Data Sources
1. **Hyperliquid API** - OHLCV data, account info, trade execution
2. **Custom API** (optioneel) - Liquidatie data, funding rates
3. **DeepSeek AI** - Trading analyse en beslissingen

### Autonomous Execution
- Main loop draait elke 15 minuten (configurabel)
- Agents handelen errors gracefully en continue execution
- Keyboard interrupt voor graceful shutdown
- Alle agents loggen naar console (termcolor)
- Database audit trail van alle beslissingen

### Volume Profile Strategy
1. **Profile Development Check**:
   - 50-120 candle lookback
   - POC drift < 0.3%
   - Skewness check: |skew| ≤ 0.25
   - Kurtosis check: 2.5 ≤ kurt ≤ 3.5
   - Development score > 75%

2. **Entry Conditions**:
   - **LONG**: Price wicks to -1σ or -2σ, closes inside value area
   - **SHORT**: Price wicks to +1σ or +2σ, closes inside value area
   - ATR between 0.15%-0.55%

3. **Exit Conditions**:
   - Take Profit: 0.9× distance to POC
   - Stop Loss: Outside ±2σ
   - Timeout: 15 candles

4. **DeepSeek Validation**:
   - Risk/Reward minimum 2:1
   - Volume profile quality > 75%
   - Market context check
   - Leverage appropriateness

## Common Patterns

### Adding New Agent
1. Create `src/agents/your_agent.py`
2. Implement standalone execution logic
3. Add to `ACTIVE_AGENTS` in `main.py` if needed
4. Use `model_factory.get_model("deepseek")` voor AI
5. Store results in `src/data/your_agent/`

### Database Logging
```python
from src.database import TradingDatabase

db = TradingDatabase()

# Log AI decision
decision_id = db.log_ai_decision(
    prompt=prompt_text,
    response=ai_response,
    market_snapshot=data_dict,
    capital=1000,
    model="deepseek-reasoner"
)

# Log trade
trade_id = db.log_trade(
    decision_id=decision_id,
    symbol="BTC",
    action="LONG",
    size=100,
    leverage=5,
    entry_price=67000,
    stop_loss=66000,
    take_profit=68000,
    strategy="volume_profile",
    confidence=85.0,
    timeframe="5m",
    timeout_candles=15
)
```

### Market Data ophalen
```python
import nice_funcs_hl as hl

# Get OHLCV data
df = hl.get_data(
    symbol="BTC",
    timeframe='5m',
    bars=170,
    add_indicators=True
)

# Current price
current_price = df['close'].iloc[-1]
```

## Project Philosophy

Dit is een **educatief portfolio project** om te demonstreren:
- AI-driven trading systemen
- Multi-agent architectuur
- Risk management implementatie
- Database design voor trading
- API integratie (DeepSeek, Hyperliquid)

**Disclaimer**: Geen garanties op winstgevendheid. Substantieel risico van verlies. Alleen voor educatieve doeleinden.

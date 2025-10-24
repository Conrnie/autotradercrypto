"""
Trading Database Schema
SQLite database for position tracking, trade history, and performance analytics
"""

import sqlite3
import os
from datetime import datetime
from typing import Dict, List, Optional
import json
from termcolor import cprint


class TradingDatabase:
    """Database manager for trading system"""

    def __init__(self, db_path: str = "src/data/trading.db"):
        """Initialize database connection"""
        self.db_path = db_path

        # Create directory if it doesn't exist
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # Initialize database
        self._init_database()

        cprint(f"✅ Database initialized: {db_path}", "green")

    def _init_database(self):
        """Create all tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # AI Decisions Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ai_decisions (
                id TEXT PRIMARY KEY,
                prompt TEXT NOT NULL,
                response TEXT NOT NULL,
                market_snapshot TEXT,
                capital_at_decision REAL NOT NULL,
                model_used TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Market Data Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS market_data (
                id TEXT PRIMARY KEY,
                symbol TEXT NOT NULL,
                price REAL NOT NULL,
                change_24h_pct REAL DEFAULT 0,
                volume REAL DEFAULT 0,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_market_data_symbol_timestamp ON market_data (symbol, timestamp DESC)")

        # Performance Log Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS performance_log (
                id TEXT PRIMARY KEY,
                capital REAL NOT NULL,
                total_trades INTEGER DEFAULT 0,
                winning_trades INTEGER DEFAULT 0,
                losing_trades INTEGER DEFAULT 0,
                total_pnl REAL DEFAULT 0,
                return_pct REAL DEFAULT 0,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_performance_log_timestamp ON performance_log (timestamp DESC)")

        # Trades Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trades (
                id TEXT PRIMARY KEY,
                decision_id TEXT,
                symbol TEXT NOT NULL,
                action TEXT NOT NULL,
                size REAL NOT NULL,
                leverage REAL DEFAULT 1,
                entry_price REAL NOT NULL,
                stop_loss REAL,
                take_profit REAL,
                strategy TEXT,
                confidence REAL,
                status TEXT DEFAULT 'open',
                exit_price REAL,
                pnl REAL DEFAULT 0,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                exit_strategy TEXT,
                exit_conditions TEXT,
                target_prices TEXT,
                timeout_candles INTEGER,
                candles_held INTEGER DEFAULT 0,
                timeframe TEXT,
                FOREIGN KEY (decision_id) REFERENCES ai_decisions(id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_symbol ON trades (symbol)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_status ON trades (status)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_trades_timestamp ON trades (timestamp DESC)")

        # Trading Config Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS trading_config (
                id TEXT PRIMARY KEY,
                initial_capital REAL NOT NULL DEFAULT 1000,
                max_leverage INTEGER NOT NULL DEFAULT 20,
                max_position_size_pct REAL NOT NULL DEFAULT 10.0,
                poll_interval_seconds INTEGER NOT NULL DEFAULT 900,
                is_active BOOLEAN DEFAULT 1,
                ai_model TEXT DEFAULT 'deepseek-reasoner',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Position Monitoring Table (new - for tracking position updates)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS position_updates (
                id TEXT PRIMARY KEY,
                trade_id TEXT NOT NULL,
                current_price REAL NOT NULL,
                unrealized_pnl REAL,
                candles_held INTEGER,
                timestamp TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (trade_id) REFERENCES trades(id)
            )
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_position_updates_trade_id ON position_updates (trade_id, timestamp DESC)")

        conn.commit()
        conn.close()

    def log_ai_decision(self, prompt: str, response: str, market_snapshot: Dict,
                       capital: float, model: str) -> str:
        """Log an AI decision"""
        import uuid
        decision_id = str(uuid.uuid4())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Convert market_snapshot to JSON, handling boolean, numpy types, and other objects
        def convert_to_serializable(obj):
            """Convert non-serializable objects to serializable format"""
            # Handle numpy types
            if hasattr(obj, 'item'):  # numpy scalar
                return obj.item()
            elif isinstance(obj, bool):
                return obj
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(item) for item in obj]
            elif isinstance(obj, (str, int, float, type(None))):
                return obj
            else:
                # Try to convert to string as fallback
                return str(obj)

        serializable_snapshot = convert_to_serializable(market_snapshot)
        snapshot_json = json.dumps(serializable_snapshot)

        cursor.execute("""
            INSERT INTO ai_decisions (id, prompt, response, market_snapshot, capital_at_decision, model_used, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (decision_id, prompt, response, snapshot_json, capital, model, datetime.now().isoformat()))

        conn.commit()
        conn.close()

        return decision_id

    def log_trade(self, decision_id: str, symbol: str, action: str, size: float,
                  leverage: float, entry_price: float, stop_loss: float, take_profit: float,
                  strategy: str, confidence: float, timeframe: str, timeout_candles: int,
                  exit_conditions: Dict = None) -> str:
        """Log a new trade"""
        import uuid
        trade_id = str(uuid.uuid4())

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO trades (id, decision_id, symbol, action, size, leverage, entry_price,
                              stop_loss, take_profit, strategy, confidence, status, timestamp,
                              exit_conditions, timeout_candles, timeframe)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'open', ?, ?, ?, ?)
        """, (trade_id, decision_id, symbol, action, size, leverage, entry_price,
              stop_loss, take_profit, strategy, confidence, datetime.now().isoformat(),
              json.dumps(exit_conditions) if exit_conditions else None, timeout_candles, timeframe))

        conn.commit()
        conn.close()

        cprint(f"✅ Trade logged: {symbol} {action} at ${entry_price:.2f}", "green")

        return trade_id

    def update_trade(self, trade_id: str, exit_price: float, pnl: float,
                    exit_strategy: str, status: str = 'closed'):
        """Update trade with exit information"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE trades
            SET exit_price = ?, pnl = ?, exit_strategy = ?, status = ?
            WHERE id = ?
        """, (exit_price, pnl, exit_strategy, status, trade_id))

        conn.commit()
        conn.close()

        cprint(f"✅ Trade updated: {trade_id} - PnL: ${pnl:.2f}", "green")

    def log_position_update(self, trade_id: str, current_price: float,
                           unrealized_pnl: float, candles_held: int):
        """Log a position monitoring update"""
        import uuid

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO position_updates (id, trade_id, current_price, unrealized_pnl, candles_held, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), trade_id, current_price, unrealized_pnl, candles_held, datetime.now().isoformat()))

        # Also update candles_held in trades table
        cursor.execute("""
            UPDATE trades SET candles_held = ? WHERE id = ?
        """, (candles_held, trade_id))

        conn.commit()
        conn.close()

    def get_open_positions(self) -> List[Dict]:
        """Get all open positions"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM trades WHERE status = 'open' ORDER BY timestamp DESC
        """)

        positions = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return positions

    def get_position_by_symbol(self, symbol: str) -> Optional[Dict]:
        """Get open position for a specific symbol"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM trades WHERE symbol = ? AND status = 'open' LIMIT 1
        """, (symbol,))

        row = cursor.fetchone()
        position = dict(row) if row else None

        conn.close()

        return position

    def log_performance(self, capital: float, total_trades: int, winning_trades: int,
                       losing_trades: int, total_pnl: float, return_pct: float):
        """Log performance snapshot"""
        import uuid

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO performance_log (id, capital, total_trades, winning_trades, losing_trades,
                                        total_pnl, return_pct, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(uuid.uuid4()), capital, total_trades, winning_trades, losing_trades,
              total_pnl, return_pct, datetime.now().isoformat()))

        conn.commit()
        conn.close()

    def get_latest_performance(self) -> Optional[Dict]:
        """Get latest performance snapshot"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM performance_log ORDER BY timestamp DESC LIMIT 1
        """)

        row = cursor.fetchone()
        perf = dict(row) if row else None

        conn.close()

        return perf

    def get_trade_history(self, limit: int = 100) -> List[Dict]:
        """Get recent trade history"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM trades ORDER BY timestamp DESC LIMIT ?
        """, (limit,))

        trades = [dict(row) for row in cursor.fetchall()]

        conn.close()

        return trades

    def get_current_capital(self) -> float:
        """Get current capital from latest performance log"""
        perf = self.get_latest_performance()
        if perf:
            return perf['capital']

        # If no performance log, return initial capital from config
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT initial_capital FROM trading_config LIMIT 1")
        row = cursor.fetchone()
        conn.close()

        return row[0] if row else 1000.0

    def close_connection(self):
        """Close database connection"""
        pass  # SQLite connections are closed after each operation


# Test the database
if __name__ == "__main__":
    cprint("\n🧪 Testing Trading Database\n", "cyan", attrs=['bold'])

    db = TradingDatabase("src/data/trading_test.db")

    # Test logging
    decision_id = db.log_ai_decision(
        prompt="Test prompt",
        response="APPROVE",
        market_snapshot={"BTC": 45000},
        capital=1000,
        model="deepseek-reasoner"
    )

    trade_id = db.log_trade(
        decision_id=decision_id,
        symbol="BTC",
        action="LONG",
        size=50,
        leverage=5,
        entry_price=45000,
        stop_loss=44700,
        take_profit=45200,
        strategy="volume_profile",
        confidence=85.5,
        timeframe="1m",
        timeout_candles=15,
        exit_conditions={"timeout": 15, "tp": 45200, "sl": 44700}
    )

    cprint(f"\n✅ Created decision: {decision_id}", "green")
    cprint(f"✅ Created trade: {trade_id}", "green")

    # Test retrieving
    positions = db.get_open_positions()
    cprint(f"\n📊 Open positions: {len(positions)}", "cyan")

    # Test updating
    db.log_position_update(trade_id, 45100, 100, 5)
    cprint(f"✅ Logged position update", "green")

    # Close trade
    db.update_trade(trade_id, 45200, 200, "take_profit")
    cprint(f"✅ Closed trade with profit", "green")

    cprint("\n✅ Database test complete!\n", "green", attrs=['bold'])

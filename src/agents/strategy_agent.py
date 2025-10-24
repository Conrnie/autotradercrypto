"""
Strategy Agent
Handles Volume Profile Mean Reversion strategy execution across multiple symbols and timeframes
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
from termcolor import cprint
import time
from datetime import datetime
from strategies.volume_profile_strategy import VolumeProfileStrategy
from database import TradingDatabase


class StrategyAgent:
    def __init__(self):
        """Initialize the Strategy Agent with Volume Profile strategies"""
        cprint("\n📊 Strategy Agent Initializing...", "cyan", attrs=['bold'])

        self.db = TradingDatabase()
        self.strategies = {}
        self.active_positions = {}  # Track open positions per symbol

        if not ENABLE_STRATEGIES:
            cprint("⚠️ Strategy Agent is disabled in config.py", "yellow")
            return

        # Initialize Volume Profile strategies for each symbol and timeframe
        if STRATEGY_TYPE == 'volume_profile':
            cprint(f"\n📊 Initializing Volume Profile strategies:", "cyan")
            cprint(f"   Symbols: {len(HYPERLIQUID_SYMBOLS)} symbols", "cyan")
            cprint(f"   Timeframes: {STRATEGY_TIMEFRAMES}", "cyan")

            for symbol in HYPERLIQUID_SYMBOLS:
                self.strategies[symbol] = {}
                for timeframe in STRATEGY_TIMEFRAMES:
                    strategy = VolumeProfileStrategy(
                        symbol=symbol,
                        timeframe=timeframe,
                        lookback_min=VP_LOOKBACK_MIN,
                        lookback_max=VP_LOOKBACK_MAX,
                        tp_fraction=VP_TP_FRACTION,
                        atr_min=VP_ATR_MIN,
                        atr_max=VP_ATR_MAX,
                        timeout_candles=VP_TIMEOUT_CANDLES
                    )
                    self.strategies[symbol][timeframe] = strategy
                    cprint(f"   ✅ {symbol} {timeframe}", "green")

            cprint(f"\n✅ Loaded {len(self.strategies)} symbols × {len(STRATEGY_TIMEFRAMES)} timeframes = {len(self.strategies) * len(STRATEGY_TIMEFRAMES)} strategies", "green")

        cprint("\n🚀 Strategy Agent ready to scan markets!", "cyan", attrs=['bold'])

    def run(self):
        """
        Main execution loop for strategy agent
        Scans all symbols and timeframes for signals
        """
        try:
            if not ENABLE_STRATEGIES:
                return

            cprint("\n" + "="*80, "cyan")
            cprint("🔍 STRATEGY AGENT SCAN CYCLE", "cyan", attrs=['bold'])
            cprint(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", "cyan")
            cprint("="*80, "cyan")

            all_signals = []

            # Scan each symbol across all timeframes
            for symbol in HYPERLIQUID_SYMBOLS:
                cprint(f"\n{'─'*80}", "cyan")
                cprint(f"📊 Scanning {symbol}", "cyan", attrs=['bold'])
                cprint(f"{'─'*80}", "cyan")

                # Check database for existing open position
                existing_position = self.db.get_position_by_symbol(symbol)
                if existing_position:
                    cprint(f"⚠️ {symbol} already has an open position (ID: {existing_position['id'][:8]}...), skipping new signals", "yellow")
                    continue

                # Collect signals from all timeframes for this symbol
                symbol_signals = []

                for timeframe in STRATEGY_TIMEFRAMES:
                    strategy = self.strategies[symbol][timeframe]

                    try:
                        signal = strategy.generate_signals()

                        if signal and signal['direction'] != 'NEUTRAL':
                            symbol_signals.append(signal)
                            cprint(f"\n✨ Signal found on {timeframe}!", "green", attrs=['bold'])

                    except Exception as e:
                        cprint(f"❌ Error generating signal for {symbol} {timeframe}: {e}", "red")
                        continue

                # If we have signals from multiple timeframes, prioritize or combine
                if symbol_signals:
                    # Use the highest confidence signal
                    best_signal = max(symbol_signals, key=lambda x: x['confidence'])
                    all_signals.append(best_signal)

                    cprint(f"\n🎯 Best signal for {symbol}:", "green", attrs=['bold'])
                    cprint(f"   Timeframe: {best_signal['timeframe']}", "green")
                    cprint(f"   Direction: {best_signal['direction']}", "green")
                    cprint(f"   Confidence: {best_signal['confidence']:.1f}%", "green")
                    cprint(f"   Leverage: {best_signal['leverage']}x", "green")

                    # Add to pending signals for Trading Agent confirmation
                    all_signals.append(best_signal)

                # Add delay to avoid Hyperliquid API rate limiting (after each symbol)
                time.sleep(2)  # 2 seconds between symbols to avoid 429 errors

            # Summary
            cprint(f"\n{'='*80}", "cyan")
            cprint(f"📊 SCAN SUMMARY", "cyan", attrs=['bold'])
            cprint(f"   Total signals generated: {len(all_signals)}", "cyan")
            cprint(f"   LONG signals: {sum(1 for s in all_signals if s['direction'] == 'LONG')}", "green")
            cprint(f"   SHORT signals: {sum(1 for s in all_signals if s['direction'] == 'SHORT')}", "red")
            cprint(f"{'='*80}\n", "cyan")

            return all_signals

        except Exception as e:
            cprint(f"\n❌ Error in strategy agent run: {e}", "red")
            import traceback
            traceback.print_exc()
            return []

    def get_signals(self, symbol: str = None):
        """
        Get signals for a specific symbol or all symbols

        Args:
            symbol: Optional specific symbol to analyze

        Returns:
            list: List of trading signals
        """
        try:
            if symbol:
                # Analyze specific symbol
                cprint(f"\n🔍 Analyzing {symbol}...", "cyan")

                if symbol not in self.strategies:
                    cprint(f"❌ {symbol} not in configured strategies", "red")
                    return []

                signals = []
                for timeframe in STRATEGY_TIMEFRAMES:
                    strategy = self.strategies[symbol][timeframe]
                    signal = strategy.generate_signals()

                    if signal and signal['direction'] != 'NEUTRAL':
                        signals.append(signal)

                return signals
            else:
                # Run full scan
                return self.run()

        except Exception as e:
            cprint(f"❌ Error getting signals: {e}", "red")
            return []

    def mark_position_opened(self, symbol: str, signal: dict):
        """Mark a position as opened to prevent duplicate entries"""
        self.active_positions[symbol] = {
            'opened_at': datetime.now(),
            'signal': signal
        }
        cprint(f"✅ Marked {symbol} as having active position", "green")

    def mark_position_closed(self, symbol: str):
        """Mark a position as closed"""
        if symbol in self.active_positions:
            del self.active_positions[symbol]
            cprint(f"✅ Marked {symbol} position as closed", "green")

    def check_position_timeouts(self):
        """Check if any positions have exceeded timeout and should be closed"""
        # This will be implemented with position management
        pass


# Test the agent
if __name__ == "__main__":
    cprint("\n🧪 Strategy Agent Test\n", "cyan", attrs=['bold'])

    agent = StrategyAgent()

    if ENABLE_STRATEGIES:
        cprint("\n📊 Running strategy scan...\n", "cyan")
        signals = agent.run()

        if signals:
            cprint(f"\n✅ Generated {len(signals)} signals!", "green")
            for signal in signals:
                cprint(f"\n{signal['symbol']} {signal['direction']}:", "cyan")
                cprint(f"  Timeframe: {signal['timeframe']}", "cyan")
                cprint(f"  Confidence: {signal['confidence']:.1f}%", "cyan")
                cprint(f"  Entry: ${signal['entry_price']:.2f}", "cyan")
                cprint(f"  Target: ${signal['target_price']:.2f}", "cyan")
                cprint(f"  Stop: ${signal['stop_loss']:.2f}", "cyan")
                cprint(f"  Leverage: {signal['leverage']}x", "cyan")
        else:
            cprint("\n⚠️ No signals generated", "yellow")
    else:
        cprint("\n⚠️ Strategies disabled in config", "yellow")

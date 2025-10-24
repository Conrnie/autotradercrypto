"""
Position Manager
Monitors open positions and manages exits (TP/SL/Timeout)
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from termcolor import cprint
from datetime import datetime, timedelta
import json
from typing import Dict, List, Optional

from database import TradingDatabase
from hyperliquid_executor import HyperliquidExecutor
from models.model_factory import ModelFactory
from config import *
import nice_funcs_hl as hl


class PositionManager:
    """Manages and monitors all open trading positions"""

    def __init__(self):
        """Initialize Position Manager"""
        cprint("\n📊 Position Manager Initializing...", "cyan", attrs=['bold'])

        self.db = TradingDatabase()
        self.executor = HyperliquidExecutor()

        # Initialize DeepSeek for exit confirmation
        try:
            self.model_factory = ModelFactory()
            self.model = self.model_factory.create_model(AI_MODEL_TYPE)
            cprint(f"✅ DeepSeek AI loaded for exit confirmation", "green")
        except Exception as e:
            cprint(f"⚠️ Could not load DeepSeek: {e}", "yellow")
            self.model = None

        cprint("🚀 Position Manager ready to monitor positions!", "cyan", attrs=['bold'])

    def get_current_price_and_candles(self, symbol: str, timeframe: str, entry_timestamp: str) -> tuple:
        """
        Get current price and count candles since entry

        Returns:
            (current_price, candles_held)
        """
        try:
            # Get current price
            current_price = self.executor.get_current_price(symbol)
            if not current_price:
                # Fallback to OHLCV data
                df = hl.get_ohlcv_data(symbol, timeframe, lookback=2)
                if df is not None and len(df) > 0:
                    current_price = df['close'].iloc[-1]
                else:
                    return None, None

            # Calculate candles held
            entry_time = datetime.fromisoformat(entry_timestamp)
            current_time = datetime.now()
            time_diff = current_time - entry_time

            # Convert time difference to candles based on timeframe
            if timeframe == '1m':
                candles_held = int(time_diff.total_seconds() / 60)
            elif timeframe == '5m':
                candles_held = int(time_diff.total_seconds() / 300)
            elif timeframe == '15m':
                candles_held = int(time_diff.total_seconds() / 900)
            else:
                candles_held = 0

            return current_price, candles_held

        except Exception as e:
            cprint(f"⚠️ Error getting price/candles: {e}", "yellow")
            return None, None

    def check_exit_conditions(self, position: Dict, current_price: float, candles_held: int) -> tuple:
        """
        Check if position should be exited

        Returns:
            (should_exit: bool, exit_reason: str)
        """
        try:
            # Parse exit conditions
            exit_conditions = json.loads(position['exit_conditions']) if position['exit_conditions'] else {}

            # Check Take Profit
            take_profit = position['take_profit']
            if take_profit:
                if position['action'] == 'LONG' and current_price >= take_profit:
                    return True, "take_profit"
                elif position['action'] == 'SHORT' and current_price <= take_profit:
                    return True, "take_profit"

            # Check Stop Loss
            stop_loss = position['stop_loss']
            if stop_loss:
                if position['action'] == 'LONG' and current_price <= stop_loss:
                    return True, "stop_loss"
                elif position['action'] == 'SHORT' and current_price >= stop_loss:
                    return True, "stop_loss"

            # Check Timeout
            timeout_candles = position['timeout_candles']
            if timeout_candles and candles_held >= timeout_candles:
                return True, "timeout"

            return False, None

        except Exception as e:
            cprint(f"⚠️ Error checking exit conditions: {e}", "yellow")
            return False, None

    def ask_deepseek_to_exit(self, position: Dict, current_price: float,
                             unrealized_pnl: float, candles_held: int) -> Dict:
        """
        Ask DeepSeek AI if we should exit this position

        Returns:
            dict: {'should_exit': bool, 'reasoning': str, 'confidence': float}
        """
        if not self.model:
            # If DeepSeek not available, follow mechanical rules
            return {'should_exit': False, 'reasoning': 'AI not available', 'confidence': 0}

        try:
            system_prompt = """You are DeepSeek, monitoring an open trading position.

Your task: Decide if we should EXIT this position NOW or HOLD it.

Consider:
1. Unrealized PnL - Are we at a good profit/loss point?
2. Time in trade - Has the setup played out?
3. Distance to targets - Are we close to TP/SL?
4. Mean reversion logic - Did price revert to POC already?

Response Format:
Line 1: EXIT or HOLD
Line 2-N: Your reasoning

Be decisive. Protect capital but don't exit winners early."""

            user_content = f"""
POSITION MONITORING REQUEST

Symbol: {position['symbol']}
Direction: {position['action']}
Timeframe: {position['timeframe']}

ENTRY:
- Entry Price: ${position['entry_price']:.2f}
- Entry Time: {position['timestamp']}
- Leverage: {position['leverage']}x

CURRENT STATUS:
- Current Price: ${current_price:.2f}
- Unrealized PnL: ${unrealized_pnl:.2f}
- Candles Held: {candles_held}/{position['timeout_candles']}
- Time in Trade: {candles_held * (1 if position['timeframe'] == '1m' else 5)} minutes

EXIT TARGETS:
- Take Profit: ${position['take_profit']:.2f}
- Stop Loss: ${position['stop_loss']:.2f}

STRATEGY: {position['strategy']}

Should we EXIT now or HOLD this position?
"""

            response = self.model.generate_response(
                system_prompt=system_prompt,
                user_content=user_content,
                temperature=0.3,
                max_tokens=1024
            )

            lines = response.strip().split('\n')
            decision = lines[0].strip().upper()
            reasoning = '\n'.join(lines[1:]).strip()

            should_exit = 'EXIT' in decision

            return {
                'should_exit': should_exit,
                'reasoning': reasoning,
                'confidence': 80 if should_exit else 20
            }

        except Exception as e:
            cprint(f"⚠️ Error asking DeepSeek: {e}", "yellow")
            return {'should_exit': False, 'reasoning': f'AI error: {e}', 'confidence': 0}

    def monitor_position(self, position: Dict) -> Optional[Dict]:
        """
        Monitor a single position

        Returns:
            Dict with exit action if position should be closed, None otherwise
        """
        try:
            symbol = position['symbol']
            trade_id = position['id']

            cprint(f"\n{'─'*80}", "cyan")
            cprint(f"📊 Monitoring {symbol} {position['action']}", "cyan", attrs=['bold'])
            cprint(f"{'─'*80}", "cyan")

            # Get current price and candles held
            current_price, candles_held = self.get_current_price_and_candles(
                symbol,
                position['timeframe'],
                position['timestamp']
            )

            if current_price is None:
                cprint(f"⚠️ Could not get current price for {symbol}", "yellow")
                return None

            # Calculate unrealized PnL
            entry_price = position['entry_price']
            size = position['size']
            leverage = position['leverage']

            if position['action'] == 'LONG':
                price_change_pct = ((current_price - entry_price) / entry_price) * 100
                unrealized_pnl = size * (current_price - entry_price) / entry_price * leverage
            else:  # SHORT
                price_change_pct = ((entry_price - current_price) / entry_price) * 100
                unrealized_pnl = size * (entry_price - current_price) / entry_price * leverage

            cprint(f"Entry: ${entry_price:.2f} | Current: ${current_price:.2f}", "cyan")
            cprint(f"PnL: ${unrealized_pnl:.2f} ({price_change_pct:+.2f}%)",
                   "green" if unrealized_pnl > 0 else "red")
            cprint(f"Candles: {candles_held}/{position['timeout_candles']}", "cyan")

            # Log position update
            self.db.log_position_update(trade_id, current_price, unrealized_pnl, candles_held)

            # Check mechanical exit conditions (TP/SL/Timeout)
            should_exit, exit_reason = self.check_exit_conditions(position, current_price, candles_held)

            if should_exit:
                cprint(f"\n⚠️ Exit condition triggered: {exit_reason.upper()}", "yellow", attrs=['bold'])

                # Ask DeepSeek for confirmation
                if AI_CONFIRMATION_REQUIRED:
                    cprint(f"\n🤖 Asking DeepSeek to confirm exit...", "yellow")
                    ai_decision = self.ask_deepseek_to_exit(position, current_price, unrealized_pnl, candles_held)

                    cprint(f"\nDeepSeek Decision: {'EXIT' if ai_decision['should_exit'] else 'HOLD'}", "yellow")
                    cprint(f"Reasoning: {ai_decision['reasoning']}", "white")

                    if not ai_decision['should_exit']:
                        cprint(f"\n⛔ DeepSeek overrode exit - Holding position", "yellow")
                        return None

                    exit_reason = f"{exit_reason}_ai_confirmed"

                # Exit approved
                return {
                    'trade_id': trade_id,
                    'symbol': symbol,
                    'action': 'CLOSE',
                    'exit_price': current_price,
                    'pnl': unrealized_pnl,
                    'exit_reason': exit_reason,
                    'candles_held': candles_held
                }

            cprint(f"\n✅ Position healthy - Continuing to monitor", "green")
            return None

        except Exception as e:
            cprint(f"❌ Error monitoring position: {e}", "red")
            import traceback
            traceback.print_exc()
            return None

    def execute_exit(self, exit_action: Dict) -> bool:
        """Execute position exit"""
        try:
            symbol = exit_action['symbol']
            trade_id = exit_action['trade_id']
            exit_price = exit_action['exit_price']
            pnl = exit_action['pnl']
            exit_reason = exit_action['exit_reason']

            cprint(f"\n{'='*80}", "yellow")
            cprint(f"📤 EXECUTING EXIT", "yellow", attrs=['bold'])
            cprint(f"{'='*80}", "yellow")
            cprint(f"Symbol: {symbol}", "yellow")
            cprint(f"Exit Price: ${exit_price:.2f}", "yellow")
            cprint(f"PnL: ${pnl:.2f}", "green" if pnl > 0 else "red")
            cprint(f"Reason: {exit_reason}", "yellow")

            # Close position on Hyperliquid
            result = self.executor.close_position(symbol)

            if result and result['success']:
                # Update database
                self.db.update_trade(
                    trade_id=trade_id,
                    exit_price=exit_price,
                    pnl=pnl,
                    exit_strategy=exit_reason,
                    status='closed'
                )

                cprint(f"\n✅ Position closed successfully!", "green", attrs=['bold'])
                cprint(f"{'='*80}\n", "yellow")

                return True
            else:
                cprint(f"\n❌ Failed to close position on exchange", "red")
                return False

        except Exception as e:
            cprint(f"❌ Error executing exit: {e}", "red")
            return False

    def run(self) -> Dict:
        """
        Main execution: Monitor all open positions

        Returns:
            Dict with summary of actions taken
        """
        try:
            cprint("\n" + "="*80, "cyan")
            cprint("🔍 POSITION MONITORING CYCLE", "cyan", attrs=['bold'])
            cprint("="*80, "cyan")

            # Get all open positions from database
            open_positions = self.db.get_open_positions()

            if not open_positions:
                cprint("\n⚪ No open positions to monitor\n", "white")
                return {'positions_monitored': 0, 'exits_executed': 0}

            cprint(f"\n📊 Monitoring {len(open_positions)} open positions...\n", "cyan")

            exits_executed = 0

            for position in open_positions:
                # Monitor this position
                exit_action = self.monitor_position(position)

                if exit_action:
                    # Execute the exit
                    success = self.execute_exit(exit_action)
                    if success:
                        exits_executed += 1

            # Summary
            cprint(f"\n{'='*80}", "cyan")
            cprint(f"📊 MONITORING SUMMARY", "cyan", attrs=['bold'])
            cprint(f"   Positions monitored: {len(open_positions)}", "cyan")
            cprint(f"   Exits executed: {exits_executed}", "green" if exits_executed > 0 else "cyan")
            cprint(f"{'='*80}\n", "cyan")

            return {
                'positions_monitored': len(open_positions),
                'exits_executed': exits_executed
            }

        except Exception as e:
            cprint(f"❌ Error in position monitoring: {e}", "red")
            import traceback
            traceback.print_exc()
            return {'positions_monitored': 0, 'exits_executed': 0, 'error': str(e)}


# Test the position manager
if __name__ == "__main__":
    cprint("\n🌙 Testing Position Manager\n", "cyan", attrs=['bold'])

    manager = PositionManager()

    cprint("\n📊 Running monitoring cycle...\n", "cyan")
    result = manager.run()

    cprint(f"\n✅ Test complete!", "green")
    cprint(f"   Result: {result}", "cyan")

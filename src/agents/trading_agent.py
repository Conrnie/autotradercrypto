"""
Trading Agent (met Database & Executie)
Handles DeepSeek AI confirmation and executes trades on Hyperliquid
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
from termcolor import cprint
import json
from models.model_factory import model_factory
from datetime import datetime
from database import TradingDatabase
from hyperliquid_executor import HyperliquidExecutor


class TradingAgent:
    def __init__(self):
        """Initialize Trading Agent with DeepSeek AI, Database, and Executor"""
        cprint("\n🌙 Moon Dev's Trading Agent Initializing...", "cyan", attrs=['bold'])

        # Initialize database
        self.db = TradingDatabase()

        # Initialize Hyperliquid executor
        self.executor = HyperliquidExecutor()

        # Use DeepSeek model via ModelFactory singleton
        try:
            self.model = model_factory.get_model("deepseek")
            if not self.model:
                raise ValueError("DeepSeek model not available")
            cprint(f"✅ DeepSeek AI model loaded: {AI_MODEL}", "green")
        except Exception as e:
            cprint(f"❌ Failed to load DeepSeek model: {e}", "red")
            raise

        cprint("🚀 Trading Agent ready for AI confirmation & execution!", "cyan", attrs=['bold'])

    def analyze_and_confirm_trade(self, signal: dict, liquidation_context: dict = None) -> dict:
        """
        Use DeepSeek to analyze volume profile signal and decide whether to execute

        Args:
            signal: Trading signal from Volume Profile strategy
            liquidation_context: Optional liquidation data for additional context

        Returns:
            dict: {
                'approved': bool,
                'reasoning': str,
                'confidence': float,
                'adjusted_leverage': int,
                'adjusted_size_pct': float,
                'decision_id': str
            }
        """
        try:
            cprint(f"\n{'='*80}", "yellow")
            cprint(f"🤖 DEEPSEEK AI TRADE ANALYSIS", "yellow", attrs=['bold'])
            cprint(f"{'='*80}", "yellow")

            # Build comprehensive prompt for DeepSeek
            system_prompt = """You are DeepSeek, an advanced AI trading analyst specializing in volume profile mean reversion strategies.

Your task is to analyze trading signals from a Volume Profile Mean Reversion strategy and make a final decision on whether to execute the trade.

You must be VERY CRITICAL and only approve high-quality setups. When in doubt, REJECT the trade.

Consider:
1. Volume Profile Quality - Is the profile truly "developed"? (Score should be >75 for high confidence)
2. Mean Reversion Logic - Does the price action support mean reversion to POC?
3. Risk/Reward Ratio - Is the R:R favorable? (Minimum 2:1)
4. ATR Volatility - Is volatility in the optimal range?
5. Entry Level - Are we entering at ±1σ or ±2σ? (±2σ is better)
6. Market Context - Any liquidation data that supports/contradicts the trade?
7. Leverage Appropriateness - Is the suggested leverage reasonable?

Response Format:
Line 1: APPROVE or REJECT
Line 2-N: Your detailed reasoning

If APPROVE, you may suggest adjustments:
- ADJUST_LEVERAGE: <new_leverage> (if you think leverage should be different)
- ADJUST_SIZE: <percentage> (if position size should be reduced, e.g., 50 for half size)

Be decisive, analytical, and prioritize capital preservation."""

            # Format signal data
            user_content = f"""
TRADING SIGNAL ANALYSIS REQUEST

Symbol: {signal['symbol']}
Direction: {signal['direction']}
Timeframe: {signal['timeframe']}

VOLUME PROFILE DATA:
- Development Score: {signal['confidence']:.1f}% (developed = {signal['volume_profile']['developed']})
- POC (Point of Control): ${signal['volume_profile']['poc']:.2f}
- Value Area: ${signal['volume_profile']['value_area_low']:.2f} - ${signal['volume_profile']['value_area_high']:.2f}
- Entry Level: {signal['metadata']['entry_level']}
- Lookback Period: {signal['volume_profile']['lookback']} candles

TRADE PARAMETERS:
- Entry Price: ${signal['entry_price']:.2f}
- Target Price: ${signal['target_price']:.2f}
- Stop Loss: ${signal['stop_loss']:.2f}
- Risk/Reward Ratio: {signal['risk_reward']:.2f}
- Suggested Leverage: {signal['leverage']}x
- ATR (Volatility): {signal['atr_percent']:.3f}%

STRATEGY REASONING:
{signal['reasoning']}
"""

            # Add liquidation context if available
            if liquidation_context:
                user_content += f"""
LIQUIDATION CONTEXT:
{json.dumps(liquidation_context, indent=2)}
"""

            cprint("\n📤 Sending signal to DeepSeek for analysis...", "yellow")

            # Get current capital for decision logging
            current_capital = self.db.get_current_capital()

            # Get DeepSeek analysis
            response = self.model.generate_response(
                system_prompt=system_prompt,
                user_content=user_content,
                temperature=AI_TEMPERATURE,
                max_tokens=AI_MAX_TOKENS
            )

            cprint(f"\n📥 DeepSeek Response:", "yellow")
            cprint(f"{response}", "white")

            # Log AI decision to database
            decision_id = self.db.log_ai_decision(
                prompt=user_content,
                response=response,
                market_snapshot={
                    'symbol': signal['symbol'],
                    'price': signal['entry_price'],
                    'volume_profile': signal['volume_profile']
                },
                capital=current_capital,
                model=AI_MODEL
            )

            # Parse response
            lines = response.strip().split('\n')
            decision = lines[0].strip().upper()

            approved = 'APPROVE' in decision
            reasoning = '\n'.join(lines[1:]).strip()

            # Parse adjustments
            adjusted_leverage = signal['leverage']
            adjusted_size_pct = 100

            for line in lines:
                if 'ADJUST_LEVERAGE' in line.upper():
                    try:
                        adjusted_leverage = int(line.split(':')[1].strip())
                        cprint(f"⚙️ DeepSeek adjusted leverage: {signal['leverage']}x → {adjusted_leverage}x", "yellow")
                    except:
                        pass
                elif 'ADJUST_SIZE' in line.upper():
                    try:
                        adjusted_size_pct = int(line.split(':')[1].strip())
                        cprint(f"⚙️ DeepSeek adjusted position size: 100% → {adjusted_size_pct}%", "yellow")
                    except:
                        pass

            result = {
                'approved': approved,
                'reasoning': reasoning,
                'confidence': signal['confidence'],
                'adjusted_leverage': adjusted_leverage,
                'adjusted_size_pct': adjusted_size_pct,
                'decision_id': decision_id,
                'original_signal': signal
            }

            if approved:
                cprint(f"\n✅ TRADE APPROVED BY DEEPSEEK", "green", attrs=['bold'])
            else:
                cprint(f"\n❌ TRADE REJECTED BY DEEPSEEK", "red", attrs=['bold'])

            cprint(f"{'='*80}\n", "yellow")

            return result

        except Exception as e:
            cprint(f"❌ Error in DeepSeek analysis: {e}", "red")
            import traceback
            traceback.print_exc()

            # Default to rejection if AI fails
            return {
                'approved': False,
                'reasoning': f"AI analysis failed: {e}",
                'confidence': 0,
                'adjusted_leverage': signal.get('leverage', 1),
                'adjusted_size_pct': 100,
                'decision_id': None,
                'original_signal': signal
            }

    def execute_trade(self, signal: dict, confirmation: dict):
        """
        Execute trade on Hyperliquid and log to database

        Args:
            signal: Original trading signal
            confirmation: DeepSeek confirmation result

        Returns:
            dict: Execution result
        """
        try:
            cprint(f"\n{'='*80}", "cyan")
            cprint(f"🚀 EXECUTING TRADE", "cyan", attrs=['bold'])
            cprint(f"{'='*80}", "cyan")

            symbol = signal['symbol']
            direction = signal['direction']
            leverage = confirmation['adjusted_leverage']
            size_pct = confirmation['adjusted_size_pct']

            # Calculate position size in USD
            base_size = usd_size
            adjusted_size = base_size * (size_pct / 100)

            cprint(f"Symbol: {symbol}", "cyan")
            cprint(f"Direction: {direction}", "cyan")
            cprint(f"Entry: ${signal['entry_price']:.2f}", "cyan")
            cprint(f"Target: ${signal['target_price']:.2f}", "cyan")
            cprint(f"Stop: ${signal['stop_loss']:.2f}", "cyan")
            cprint(f"Leverage: {leverage}x", "cyan")
            cprint(f"Position Size: ${adjusted_size:.2f} ({size_pct}%)", "cyan")

            # Execute on Hyperliquid
            is_buy = (direction == 'LONG')
            result = self.executor.market_order(symbol, is_buy, adjusted_size, leverage)

            if result and result['success']:
                # Log trade to database
                trade_id = self.db.log_trade(
                    decision_id=confirmation['decision_id'],
                    symbol=symbol,
                    action=direction,
                    size=adjusted_size,
                    leverage=leverage,
                    entry_price=signal['entry_price'],
                    stop_loss=signal['stop_loss'],
                    take_profit=signal['target_price'],
                    strategy='volume_profile',
                    confidence=signal['confidence'],
                    timeframe=signal['timeframe'],
                    timeout_candles=signal['metadata'].get('timeout_candles', 15),
                    exit_conditions={
                        'take_profit': signal['target_price'],
                        'stop_loss': signal['stop_loss'],
                        'timeout_candles': signal['metadata'].get('timeout_candles', 15)
                    }
                )

                cprint(f"\n✅ Trade executed and logged successfully!", "green", attrs=['bold'])
                cprint(f"   Trade ID: {trade_id}", "green")
                cprint(f"{'='*80}\n", "cyan")

                return {
                    'success': True,
                    'trade_id': trade_id,
                    'execution_result': result,
                    'message': 'Trade executed on Hyperliquid and logged to database'
                }

            else:
                cprint(f"\n❌ Failed to execute trade on Hyperliquid", "red")
                cprint(f"{'='*80}\n", "cyan")

                return {
                    'success': False,
                    'message': 'Trade execution failed on exchange'
                }

        except Exception as e:
            cprint(f"❌ Error executing trade: {e}", "red")
            import traceback
            traceback.print_exc()

            return {
                'success': False,
                'message': str(e)
            }

    def run(self, signals: list):
        """
        Process a list of signals from Strategy Agent

        Args:
            signals: List of trading signals to evaluate

        Returns:
            list: Results of approved and executed trades
        """
        try:
            if not signals:
                cprint("\n⚠️ No signals to process", "yellow")
                return []

            cprint(f"\n🔄 Processing {len(signals)} signals...", "cyan")

            results = []

            for i, signal in enumerate(signals, 1):
                cprint(f"\n{'─'*80}", "cyan")
                cprint(f"Signal {i}/{len(signals)}: {signal['symbol']} {signal['direction']}", "cyan", attrs=['bold'])
                cprint(f"{'─'*80}", "cyan")

                # Get DeepSeek confirmation
                confirmation = self.analyze_and_confirm_trade(signal)

                if confirmation['approved']:
                    # Execute the trade
                    execution_result = self.execute_trade(signal, confirmation)
                    results.append({
                        'signal': signal,
                        'confirmation': confirmation,
                        'execution': execution_result
                    })
                else:
                    cprint(f"\n⛔ Trade rejected, moving to next signal", "red")
                    results.append({
                        'signal': signal,
                        'confirmation': confirmation,
                        'execution': None
                    })

            # Summary
            approved_count = sum(1 for r in results if r['confirmation']['approved'])
            executed_count = sum(1 for r in results if r['execution'] and r['execution']['success'])

            cprint(f"\n{'='*80}", "cyan")
            cprint(f"📊 TRADING SESSION SUMMARY", "cyan", attrs=['bold'])
            cprint(f"   Signals processed: {len(signals)}", "cyan")
            cprint(f"   Approved by DeepSeek: {approved_count}", "green")
            cprint(f"   Executed successfully: {executed_count}", "green")
            cprint(f"   Rejected: {len(signals) - approved_count}", "red")
            cprint(f"{'='*80}\n", "cyan")

            return results

        except Exception as e:
            cprint(f"❌ Error in trading agent run: {e}", "red")
            import traceback
            traceback.print_exc()
            return []


# Test the agent
if __name__ == "__main__":
    cprint("\n🌙 Moon Dev's Trading Agent Test\n", "cyan", attrs=['bold'])

    # Create a test signal
    test_signal = {
        'symbol': 'BTC',
        'direction': 'LONG',
        'timeframe': '1m',
        'confidence': 85.5,
        'entry_price': 45000,
        'target_price': 45200,
        'stop_loss': 44850,
        'leverage': 5,
        'atr_percent': 0.35,
        'risk_reward': 2.5,
        'volume_profile': {
            'poc': 45100,
            'value_area_low': 44900,
            'value_area_high': 45300,
            'developed': True,
            'lookback': 80
        },
        'metadata': {
            'entry_level': '2σ',
            'timeout_candles': 15
        },
        'reasoning': 'Price wicked to -2σ and closed back inside value area. Strong mean reversion setup.'
    }

    agent = TradingAgent()

    cprint("\n🧪 Testing DeepSeek confirmation with test signal...\n", "cyan")

    confirmation = agent.analyze_and_confirm_trade(test_signal)

    cprint(f"\n📊 Test Result:", "cyan")
    cprint(f"   Approved: {confirmation['approved']}", "cyan")
    cprint(f"   Adjusted Leverage: {confirmation['adjusted_leverage']}x", "cyan")
    cprint(f"   Position Size: {confirmation['adjusted_size_pct']}%", "cyan")

    if confirmation['approved']:
        cprint(f"\n🚀 Would execute trade (skipping in test)...", "cyan")

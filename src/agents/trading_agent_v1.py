"""
🌙 Moon Dev's Trading Agent
Handles DeepSeek AI confirmation for Volume Profile strategy signals
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import *
from termcolor import cprint
import json
from models.model_factory import ModelFactory
from datetime import datetime


class TradingAgent:
    def __init__(self):
        """Initialize Trading Agent with DeepSeek AI model"""
        cprint("\n🌙 Moon Dev's Trading Agent Initializing...", "cyan", attrs=['bold'])

        # Initialize DeepSeek model
        try:
            self.model_factory = ModelFactory()
            self.model = self.model_factory.create_model(AI_MODEL_TYPE)
            cprint(f"✅ DeepSeek AI model loaded: {AI_MODEL}", "green")
        except Exception as e:
            cprint(f"❌ Failed to load DeepSeek model: {e}", "red")
            raise

        cprint("🚀 Trading Agent ready for AI confirmation!", "cyan", attrs=['bold'])

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
                'adjusted_leverage': int (optional),
                'adjusted_position_size': float (optional)
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

            # Get DeepSeek analysis
            response = self.model.generate_response(
                system_prompt=system_prompt,
                user_content=user_content,
                temperature=AI_TEMPERATURE,
                max_tokens=AI_MAX_TOKENS
            )

            cprint(f"\n📥 DeepSeek Response:", "yellow")
            cprint(f"{response}", "white")

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
                'original_signal': signal
            }

    def execute_trade(self, signal: dict, confirmation: dict):
        """
        Execute trade on Hyperliquid testnet (placeholder)

        This will be implemented when we integrate Hyperliquid trading functions
        """
        try:
            cprint(f"\n{'='*80}", "cyan")
            cprint(f"🚀 EXECUTING TRADE", "cyan", attrs=['bold'])
            cprint(f"{'='*80}", "cyan")

            symbol = signal['symbol']
            direction = signal['direction']
            leverage = confirmation['adjusted_leverage']
            size_pct = confirmation['adjusted_size_pct']

            cprint(f"Symbol: {symbol}", "cyan")
            cprint(f"Direction: {direction}", "cyan")
            cprint(f"Entry: ${signal['entry_price']:.2f}", "cyan")
            cprint(f"Target: ${signal['target_price']:.2f}", "cyan")
            cprint(f"Stop: ${signal['stop_loss']:.2f}", "cyan")
            cprint(f"Leverage: {leverage}x", "cyan")
            cprint(f"Position Size: {size_pct}%", "cyan")

            # TODO: Integrate actual Hyperliquid trading here
            # This is where we'd call hyperliquid functions to:
            # 1. Set leverage
            # 2. Open position (market buy/sell)
            # 3. Set stop loss and take profit

            cprint(f"\n⚠️ PAPER TRADING MODE - No actual trade executed", "yellow")
            cprint(f"   (Hyperliquid testnet integration pending)", "yellow")

            # Log trade for tracking
            self._log_trade(signal, confirmation)

            cprint(f"{'='*80}\n", "cyan")

            return {
                'success': True,
                'message': 'Paper trade logged successfully'
            }

        except Exception as e:
            cprint(f"❌ Error executing trade: {e}", "red")
            return {
                'success': False,
                'message': str(e)
            }

    def _log_trade(self, signal: dict, confirmation: dict):
        """Log trade to file for tracking"""
        try:
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'symbol': signal['symbol'],
                'direction': signal['direction'],
                'timeframe': signal['timeframe'],
                'entry_price': signal['entry_price'],
                'target_price': signal['target_price'],
                'stop_loss': signal['stop_loss'],
                'leverage': confirmation['adjusted_leverage'],
                'size_pct': confirmation['adjusted_size_pct'],
                'confidence': signal['confidence'],
                'reasoning': signal['reasoning'],
                'ai_reasoning': confirmation['reasoning']
            }

            # Create log file if it doesn't exist
            log_file = 'src/data/trade_log.jsonl'
            os.makedirs(os.path.dirname(log_file), exist_ok=True)

            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')

            cprint(f"📝 Trade logged to {log_file}", "green")

        except Exception as e:
            cprint(f"⚠️ Could not log trade: {e}", "yellow")

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
            cprint(f"\n{'='*80}", "cyan")
            cprint(f"📊 TRADING SESSION SUMMARY", "cyan", attrs=['bold'])
            cprint(f"   Signals processed: {len(signals)}", "cyan")
            cprint(f"   Approved by DeepSeek: {approved_count}", "green")
            cprint(f"   Rejected by DeepSeek: {len(signals) - approved_count}", "red")
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
            'entry_level': '2σ'
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

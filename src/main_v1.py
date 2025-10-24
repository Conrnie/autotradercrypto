"""
🌙 Moon Dev's AI Trading System
Volume Profile Mean Reversion Trading with DeepSeek AI Confirmation
"""

import os
import sys
from termcolor import cprint
from dotenv import load_dotenv
import time
from datetime import datetime, timedelta
from config import *

# Add project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)

# Import agents
from agents.trading_agent import TradingAgent
from agents.risk_agent import RiskAgent
from agents.strategy_agent import StrategyAgent
from agents.liquidation_agent import LiquidationAgent

# Load environment variables
load_dotenv()

# Agent Configuration
ACTIVE_AGENTS = {
    'risk': True,         # Risk management agent
    'liquidation': True,  # Liquidation monitoring agent
    'strategy': True,     # Volume Profile strategy agent
    'trading': True,      # DeepSeek AI confirmation agent
}


def print_banner():
    """Print startup banner"""
    cprint("\n" + "="*100, "cyan")
    cprint(" ", "cyan")
    cprint("🌙 MOON DEV AI TRADING SYSTEM".center(100), "white", "on_cyan", attrs=['bold'])
    cprint(" ", "cyan")
    cprint("="*100, "cyan")
    cprint("\n📊 STRATEGY: Volume Profile Mean Reversion Scalper (RSI-Free)", "cyan", attrs=['bold'])
    cprint("🤖 AI MODEL: DeepSeek Reasoner (Confirmation Required)", "cyan", attrs=['bold'])
    cprint("💱 EXCHANGE: Hyperliquid Testnet (Paper Trading)", "cyan", attrs=['bold'])
    cprint(f"📈 SYMBOLS: {len(HYPERLIQUID_SYMBOLS)} crypto pairs", "cyan", attrs=['bold'])
    cprint(f"⏱️  TIMEFRAMES: {', '.join(STRATEGY_TIMEFRAMES)}", "cyan", attrs=['bold'])
    cprint(f"💰 CAPITAL: ${TESTNET_CAPITAL} USD (Mock)", "cyan", attrs=['bold'])
    cprint(f"📊 LEVERAGE: {HYPERLIQUID_MIN_LEVERAGE}x - {HYPERLIQUID_MAX_LEVERAGE}x (AI Decides)", "cyan", attrs=['bold'])
    cprint("="*100 + "\n", "cyan")


def run_agents():
    """Run all active agents in sequence"""
    try:
        print_banner()

        # Initialize active agents
        cprint("🔧 Initializing agents...\n", "cyan")

        risk_agent = RiskAgent() if ACTIVE_AGENTS['risk'] else None
        liquidation_agent = LiquidationAgent() if ACTIVE_AGENTS['liquidation'] else None
        strategy_agent = StrategyAgent() if ACTIVE_AGENTS['strategy'] else None
        trading_agent = TradingAgent() if ACTIVE_AGENTS['trading'] else None

        cprint("\n✅ All agents initialized successfully!\n", "green", attrs=['bold'])

        # Main trading loop
        cycle_count = 0

        while True:
            try:
                cycle_count += 1
                cprint("\n" + "="*100, "white", "on_blue")
                cprint(f"🔄 TRADING CYCLE #{cycle_count}".center(100), "white", "on_blue", attrs=['bold'])
                cprint(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(100), "white", "on_blue")
                cprint("="*100 + "\n", "white", "on_blue")

                # ========================================
                # STEP 1: Risk Management Check
                # ========================================
                if risk_agent:
                    cprint("\n🛡️  STEP 1: RISK MANAGEMENT CHECK", "cyan", attrs=['bold'])
                    cprint("─"*100 + "\n", "cyan")

                    risk_status = risk_agent.run()

                    # If risk agent says stop trading, skip this cycle
                    if risk_status and not risk_status.get('safe_to_trade', True):
                        cprint("\n⚠️  RISK AGENT HALT: Not safe to trade this cycle", "yellow", attrs=['bold'])
                        cprint("   Waiting for next cycle...\n", "yellow")
                        next_run = datetime.now() + timedelta(minutes=SLEEP_BETWEEN_RUNS_MINUTES)
                        cprint(f"😴 Sleeping until {next_run.strftime('%H:%M:%S')}\n", "cyan")
                        time.sleep(60 * SLEEP_BETWEEN_RUNS_MINUTES)
                        continue

                    cprint("\n✅ Risk check passed - Safe to trade\n", "green")

                # ========================================
                # STEP 2: Liquidation Context Analysis
                # ========================================
                liquidation_context = None

                if liquidation_agent:
                    cprint("\n📊 STEP 2: LIQUIDATION CONTEXT ANALYSIS", "cyan", attrs=['bold'])
                    cprint("─"*100 + "\n", "cyan")

                    try:
                        liquidation_context = liquidation_agent.run()
                        cprint("\n✅ Liquidation context collected\n", "green")
                    except Exception as e:
                        cprint(f"\n⚠️  Error getting liquidation data: {e}", "yellow")
                        cprint("   Continuing without liquidation context...\n", "yellow")

                # ========================================
                # STEP 3: Strategy Signal Generation
                # ========================================
                signals = []

                if strategy_agent:
                    cprint("\n🎯 STEP 3: VOLUME PROFILE SIGNAL GENERATION", "cyan", attrs=['bold'])
                    cprint("─"*100 + "\n", "cyan")

                    signals = strategy_agent.run()

                    if signals:
                        cprint(f"\n✅ Generated {len(signals)} trading signals\n", "green", attrs=['bold'])
                    else:
                        cprint("\n⚠️  No trading signals generated this cycle\n", "yellow")

                # ========================================
                # STEP 4: AI Confirmation & Execution
                # ========================================
                if trading_agent and signals:
                    cprint("\n🤖 STEP 4: DEEPSEEK AI CONFIRMATION & EXECUTION", "cyan", attrs=['bold'])
                    cprint("─"*100 + "\n", "cyan")

                    # Pass signals to trading agent for DeepSeek confirmation
                    results = trading_agent.run(signals)

                    # Summary
                    if results:
                        approved = sum(1 for r in results if r['confirmation']['approved'])
                        executed = sum(1 for r in results if r['execution'] and r['execution']['success'])

                        cprint(f"\n✅ Trading cycle complete!", "green", attrs=['bold'])
                        cprint(f"   Signals analyzed: {len(signals)}", "green")
                        cprint(f"   Approved by AI: {approved}", "green")
                        cprint(f"   Executed: {executed}\n", "green")
                    else:
                        cprint(f"\n⚠️  No trades executed this cycle\n", "yellow")

                elif not signals:
                    cprint("\n⚪ No signals to analyze - Skipping AI confirmation\n", "white")

                # ========================================
                # CYCLE COMPLETE - Sleep until next run
                # ========================================
                next_run = datetime.now() + timedelta(minutes=SLEEP_BETWEEN_RUNS_MINUTES)
                cprint("\n" + "="*100, "white", "on_green")
                cprint(f"✅ CYCLE #{cycle_count} COMPLETE".center(100), "white", "on_green", attrs=['bold'])
                cprint("="*100, "white", "on_green")

                cprint(f"\n😴 Sleeping until {next_run.strftime('%H:%M:%S')}", "cyan")
                cprint(f"   ({SLEEP_BETWEEN_RUNS_MINUTES} minutes)\n", "cyan")

                time.sleep(60 * SLEEP_BETWEEN_RUNS_MINUTES)

            except KeyboardInterrupt:
                raise  # Re-raise to outer handler

            except Exception as e:
                cprint(f"\n❌ Error in trading cycle: {str(e)}", "red")
                cprint("🔄 Continuing to next cycle in 60 seconds...\n", "yellow")
                import traceback
                traceback.print_exc()
                time.sleep(60)  # Sleep for 1 minute on error before retrying

    except KeyboardInterrupt:
        cprint("\n\n" + "="*100, "yellow")
        cprint("👋 GRACEFULLY SHUTTING DOWN...".center(100), "white", "on_yellow", attrs=['bold'])
        cprint("="*100, "yellow")
        cprint("\n🌙 Thank you for using Moon Dev AI Trading System!\n", "cyan")

    except Exception as e:
        cprint(f"\n❌ Fatal error in main loop: {str(e)}", "red")
        import traceback
        traceback.print_exc()
        raise


if __name__ == "__main__":
    # Startup checks
    cprint("\n🔍 Performing startup checks...", "cyan")

    # Check if strategies are enabled
    if not ENABLE_STRATEGIES:
        cprint("\n❌ ERROR: Strategies are disabled in config.py", "red")
        cprint("   Set ENABLE_STRATEGIES = True to run the trading system\n", "red")
        sys.exit(1)

    # Check if testnet is enabled
    if not HYPERLIQUID_TESTNET:
        cprint("\n⚠️  WARNING: Hyperliquid testnet is disabled!", "yellow", attrs=['bold'])
        cprint("   This will use REAL MONEY on mainnet!", "yellow", attrs=['bold'])
        response = input("\n   Type 'YES' to continue with mainnet, or anything else to exit: ")
        if response != 'YES':
            cprint("\n👋 Exiting for safety...\n", "cyan")
            sys.exit(0)

    # Check for required API keys
    if not os.getenv("DEEPSEEK_KEY"):
        cprint("\n❌ ERROR: DEEPSEEK_KEY not found in .env file", "red")
        cprint("   DeepSeek API key is required for AI confirmation\n", "red")
        sys.exit(1)

    # Check active agents
    active_count = sum(1 for v in ACTIVE_AGENTS.values() if v)
    if active_count == 0:
        cprint("\n❌ ERROR: No agents are enabled!", "red")
        cprint("   Enable at least one agent in ACTIVE_AGENTS\n", "red")
        sys.exit(1)

    cprint("✅ All startup checks passed!\n", "green")

    # Display active agents
    cprint("📊 Active Agents:", "cyan", attrs=['bold'])
    for agent, active in ACTIVE_AGENTS.items():
        status = "✅ ENABLED" if active else "❌ DISABLED"
        color = "green" if active else "red"
        cprint(f"   • {agent.title()}: {status}", color)

    cprint("\n🚀 Starting trading system...\n", "cyan", attrs=['bold'])

    # Run the trading system
    run_agents()

"""
Hyperliquid Executor
Handles all trade execution on Hyperliquid testnet/mainnet
"""

import os
from typing import Dict, Optional, List
from termcolor import cprint
from config import HYPERLIQUID_TESTNET
import requests
import time


class HyperliquidExecutor:
    """Executes trades on Hyperliquid"""

    def __init__(self):
        """Initialize Hyperliquid executor"""
        self.testnet = HYPERLIQUID_TESTNET

        # API endpoints
        self.info_url = "https://api.hyperliquid-testnet.xyz/info" if self.testnet else "https://api.hyperliquid.xyz/info"
        self.exchange_url = "https://api.hyperliquid-testnet.xyz/exchange" if self.testnet else "https://api.hyperliquid.xyz/exchange"

        # Get private key
        self.private_key = os.getenv("HYPER_LIQUID_KEY")
        if not self.private_key:
            raise ValueError("HYPER_LIQUID_KEY not found in environment variables")

        # Initialize account
        try:
            import eth_account
            if self.private_key.startswith("0x"):
                self.account = eth_account.Account.from_key(self.private_key)
            else:
                self.account = eth_account.Account.from_key(f"0x{self.private_key}")

            mode = "TESTNET" if self.testnet else "MAINNET"
            cprint(f"✅ Hyperliquid Executor initialized ({mode})", "green")
            cprint(f"   Address: {self.account.address}", "cyan")

        except Exception as e:
            cprint(f"❌ Failed to initialize Hyperliquid account: {e}", "red")
            raise

    def get_account_value(self) -> float:
        """Get total account value in USD"""
        try:
            response = requests.post(
                self.info_url,
                json={
                    "type": "clearinghouseState",
                    "user": self.account.address
                }
            )

            if response.status_code == 200:
                data = response.json()
                if 'marginSummary' in data:
                    return float(data['marginSummary']['accountValue'])

            return 0.0

        except Exception as e:
            cprint(f"⚠️ Error getting account value: {e}", "yellow")
            return 0.0

    def get_current_price(self, symbol: str) -> Optional[float]:
        """Get current market price for symbol"""
        try:
            response = requests.post(
                self.info_url,
                json={"type": "allMids"}
            )

            if response.status_code == 200:
                prices = response.json()
                if symbol in prices:
                    return float(prices[symbol])

            return None

        except Exception as e:
            cprint(f"⚠️ Error getting price for {symbol}: {e}", "yellow")
            return None

    def get_open_position(self, symbol: str) -> Optional[Dict]:
        """Get open position for a symbol"""
        try:
            response = requests.post(
                self.info_url,
                json={
                    "type": "clearinghouseState",
                    "user": self.account.address
                }
            )

            if response.status_code == 200:
                data = response.json()
                if 'assetPositions' in data:
                    for position in data['assetPositions']:
                        if position['position']['coin'] == symbol:
                            return {
                                'symbol': symbol,
                                'size': float(position['position']['szi']),
                                'entry_price': float(position['position']['entryPx']),
                                'unrealized_pnl': float(position['position']['unrealizedPnl']),
                                'leverage': float(position['position']['leverage']['value']),
                                'liquidation_px': float(position['position']['liquidationPx']) if 'liquidationPx' in position['position'] else None
                            }

            return None

        except Exception as e:
            cprint(f"⚠️ Error getting position for {symbol}: {e}", "yellow")
            return None

    def set_leverage(self, symbol: str, leverage: int) -> bool:
        """Set leverage for a symbol"""
        try:
            cprint(f"⚙️ Setting {symbol} leverage to {leverage}x...", "cyan")

            # Note: Actual leverage setting requires signing with eth_account
            # This is a placeholder - full implementation needs the Hyperliquid Python SDK
            # For now, we'll assume leverage is set via the UI or default

            cprint(f"✅ Leverage set (simulated)", "green")
            return True

        except Exception as e:
            cprint(f"❌ Error setting leverage: {e}", "red")
            return False

    def market_order(self, symbol: str, is_buy: bool, size_usd: float, leverage: int) -> Optional[Dict]:
        """
        Execute a market order

        Args:
            symbol: Trading symbol (e.g., 'BTC')
            is_buy: True for long, False for short
            size_usd: Position size in USD
            leverage: Leverage to use

        Returns:
            Dict with order result or None if failed
        """
        try:
            direction = "LONG" if is_buy else "SHORT"
            cprint(f"\n{'='*80}", "cyan")
            cprint(f"🚀 EXECUTING {direction} ORDER", "cyan", attrs=['bold'])
            cprint(f"{'='*80}", "cyan")
            cprint(f"Symbol: {symbol}", "cyan")
            cprint(f"Size: ${size_usd:.2f} USD", "cyan")
            cprint(f"Leverage: {leverage}x", "cyan")

            # Get current price
            current_price = self.get_current_price(symbol)
            if not current_price:
                cprint(f"❌ Could not get current price for {symbol}", "red")
                return None

            # Calculate size in contracts
            size_in_contracts = size_usd / current_price
            cprint(f"Price: ${current_price:.2f}", "cyan")
            cprint(f"Contracts: {size_in_contracts:.4f}", "cyan")

            # For testnet simulation, we'll log the order but not execute
            # Full execution requires the Hyperliquid Python SDK and proper signing
            if self.testnet:
                cprint(f"\n⚠️ TESTNET MODE - Simulating order execution", "yellow")
                cprint(f"   In production, this would execute on Hyperliquid", "yellow")

                # Simulate successful execution
                result = {
                    'success': True,
                    'symbol': symbol,
                    'direction': direction,
                    'size_usd': size_usd,
                    'size_contracts': size_in_contracts,
                    'entry_price': current_price,
                    'leverage': leverage,
                    'timestamp': time.time(),
                    'simulated': True
                }

                cprint(f"\n✅ Order simulated successfully", "green")
                cprint(f"{'='*80}\n", "cyan")

                return result

            else:
                cprint(f"\n❌ MAINNET EXECUTION NOT IMPLEMENTED", "red")
                cprint(f"   Please use testnet mode for safety", "red")
                return None

        except Exception as e:
            cprint(f"❌ Error executing market order: {e}", "red")
            import traceback
            traceback.print_exc()
            return None

    def close_position(self, symbol: str) -> Optional[Dict]:
        """Close an open position"""
        try:
            cprint(f"\n{'='*80}", "yellow")
            cprint(f"📤 CLOSING POSITION", "yellow", attrs=['bold'])
            cprint(f"{'='*80}", "yellow")
            cprint(f"Symbol: {symbol}", "yellow")

            # Get current position
            position = self.get_open_position(symbol)
            if not position:
                cprint(f"⚠️ No open position found for {symbol}", "yellow")
                return None

            cprint(f"Position size: {position['size']} contracts", "yellow")
            cprint(f"Entry price: ${position['entry_price']:.2f}", "yellow")
            cprint(f"Unrealized PnL: ${position['unrealized_pnl']:.2f}", "yellow")

            # Get current price for exit
            exit_price = self.get_current_price(symbol)
            if not exit_price:
                cprint(f"❌ Could not get current price for {symbol}", "red")
                return None

            cprint(f"Exit price: ${exit_price:.2f}", "yellow")

            # For testnet simulation
            if self.testnet:
                cprint(f"\n⚠️ TESTNET MODE - Simulating position close", "yellow")

                # Calculate realized PnL
                size = abs(position['size'])
                if position['size'] > 0:  # Long position
                    pnl = (exit_price - position['entry_price']) * size
                else:  # Short position
                    pnl = (position['entry_price'] - exit_price) * size

                result = {
                    'success': True,
                    'symbol': symbol,
                    'size': position['size'],
                    'entry_price': position['entry_price'],
                    'exit_price': exit_price,
                    'pnl': pnl,
                    'timestamp': time.time(),
                    'simulated': True
                }

                cprint(f"\n✅ Position closed successfully", "green")
                cprint(f"   Realized PnL: ${pnl:.2f}", "green" if pnl > 0 else "red")
                cprint(f"{'='*80}\n", "yellow")

                return result

            else:
                cprint(f"\n❌ MAINNET EXECUTION NOT IMPLEMENTED", "red")
                return None

        except Exception as e:
            cprint(f"❌ Error closing position: {e}", "red")
            import traceback
            traceback.print_exc()
            return None

    def get_all_positions(self) -> List[Dict]:
        """Get all open positions"""
        try:
            response = requests.post(
                self.info_url,
                json={
                    "type": "clearinghouseState",
                    "user": self.account.address
                }
            )

            if response.status_code == 200:
                data = response.json()
                positions = []

                if 'assetPositions' in data:
                    for position in data['assetPositions']:
                        positions.append({
                            'symbol': position['position']['coin'],
                            'size': float(position['position']['szi']),
                            'entry_price': float(position['position']['entryPx']),
                            'unrealized_pnl': float(position['position']['unrealizedPnl']),
                            'leverage': float(position['position']['leverage']['value'])
                        })

                return positions

            return []

        except Exception as e:
            cprint(f"⚠️ Error getting all positions: {e}", "yellow")
            return []


# Test the executor
if __name__ == "__main__":
    cprint("\n🧪 Testing Hyperliquid Executor\n", "cyan", attrs=['bold'])

    try:
        executor = HyperliquidExecutor()

        # Test getting account value
        value = executor.get_account_value()
        cprint(f"Account value: ${value:.2f}", "cyan")

        # Test getting BTC price
        btc_price = executor.get_current_price("BTC")
        if btc_price:
            cprint(f"BTC price: ${btc_price:.2f}", "cyan")

        # Test simulated order
        cprint("\n🧪 Testing simulated market order...\n", "cyan")
        result = executor.market_order("BTC", True, 50, 5)

        if result:
            cprint(f"\n✅ Test order successful!", "green")
        else:
            cprint(f"\n❌ Test order failed", "red")

    except Exception as e:
        cprint(f"\n❌ Test failed: {e}", "red")
        import traceback
        traceback.print_exc()

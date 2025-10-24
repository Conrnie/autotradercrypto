"""
Volume Profile Mean Reversion Strategy

Strategy: Developed Volume Profile Mean Reversion Scalper (RSI-Free)
Objective: Scalp mean reversion toward POC inside developed volume profile
"""

import pandas as pd
import numpy as np
from scipy import stats
from termcolor import cprint
from typing import Dict, List, Optional, Tuple
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from strategies.base_strategy import BaseStrategy
import nice_funcs_hl as hl


class VolumeProfileStrategy(BaseStrategy):
    """Volume Profile Mean Reversion Strategy for scalping"""

    def __init__(self,
                 symbol: str,
                 timeframe: str = '1m',
                 lookback_min: int = 50,
                 lookback_max: int = 120,
                 sigma_levels: List[float] = [1.0, 2.0],
                 tp_fraction: float = 0.9,
                 atr_min: float = 0.15,
                 atr_max: float = 0.55,
                 timeout_candles: int = 15):
        """
        Initialize Volume Profile Strategy

        Args:
            symbol: Trading symbol (e.g., 'BTC', 'ETH', 'SOL')
            timeframe: Candle timeframe ('1m' or '5m')
            lookback_min: Minimum lookback candles for profile (default 50)
            lookback_max: Maximum lookback candles for profile (default 120)
            sigma_levels: Sigma levels to use for entries [1.0, 2.0]
            tp_fraction: Take profit as fraction of distance to POC (default 0.9)
            atr_min: Minimum ATR % for valid setup (default 0.15%)
            atr_max: Maximum ATR % for valid setup (default 0.55%)
            timeout_candles: Max candles to hold position (default 15)
        """
        super().__init__(f"VolumeProfile_{symbol}_{timeframe}")

        self.symbol = symbol
        self.timeframe = timeframe
        self.lookback_min = lookback_min
        self.lookback_max = lookback_max
        self.sigma_levels = sigma_levels
        self.tp_fraction = tp_fraction
        self.atr_min = atr_min
        self.atr_max = atr_max
        self.timeout_candles = timeout_candles

        # Optimized lookback (will be adjusted)
        self.optimal_lookback = lookback_min

    def calculate_volume_profile(self, df: pd.DataFrame, lookback: int) -> Dict:
        """
        Calculate volume profile for given lookback period

        Returns:
            dict: {
                'poc': float,           # Point of Control (price with most volume)
                'value_area_high': float,  # +1σ
                'value_area_low': float,   # -1σ
                'sigma_2_high': float,     # +2σ
                'sigma_2_low': float,      # -2σ
                'mean_price': float,       # Volume-weighted mean
                'std_price': float,        # Standard deviation
                'developed': bool,         # Is profile developed?
                'development_score': float # Quality score 0-100
            }
        """
        try:
            if len(df) < lookback:
                return None

            # Get last N candles
            data = df.tail(lookback).copy()

            # Calculate volume-weighted price
            data['vwap'] = (data['close'] * data['volume']).cumsum() / data['volume'].cumsum()

            # Create price bins for volume profile
            num_bins = min(50, len(data) // 2)
            price_range = data['high'].max() - data['low'].min()
            bin_size = price_range / num_bins

            # Bin prices by volume
            bins = np.linspace(data['low'].min(), data['high'].max(), num_bins + 1)
            data['price_bin'] = pd.cut(data['close'], bins=bins, labels=False, include_lowest=True)

            # Calculate volume per price level
            volume_profile = data.groupby('price_bin')['volume'].sum()

            # Find POC (Point of Control - price with highest volume)
            poc_bin = volume_profile.idxmax()
            poc_price = bins[int(poc_bin)] + bin_size / 2

            # Calculate volume-weighted statistics
            total_volume = data['volume'].sum()
            weighted_prices = data['close'] * data['volume']
            mean_price = weighted_prices.sum() / total_volume

            # Calculate weighted standard deviation
            variance = ((data['close'] - mean_price) ** 2 * data['volume']).sum() / total_volume
            std_price = np.sqrt(variance)

            # Calculate value area boundaries
            value_area_high = mean_price + std_price
            value_area_low = mean_price - std_price
            sigma_2_high = mean_price + (2 * std_price)
            sigma_2_low = mean_price - (2 * std_price)

            # Check if profile is "developed"
            developed, dev_score = self._check_development(data, poc_price, mean_price, std_price)

            return {
                'poc': poc_price,
                'value_area_high': value_area_high,
                'value_area_low': value_area_low,
                'sigma_2_high': sigma_2_high,
                'sigma_2_low': sigma_2_low,
                'mean_price': mean_price,
                'std_price': std_price,
                'developed': developed,
                'development_score': dev_score,
                'lookback': lookback,
                'num_candles': len(data)
            }

        except Exception as e:
            cprint(f"❌ Error calculating volume profile: {e}", "red")
            return None

    def _check_development(self, data: pd.DataFrame, poc: float, mean: float, std: float) -> Tuple[bool, float]:
        """
        Check if volume profile is "developed" based on criteria:
        1. POC drift < 0.3% over last 10 candles
        2. |Skewness| ≤ 0.25
        3. 2.5 ≤ Kurtosis ≤ 3.5
        4. ≥65% of closes fall within ±1σ value area

        Returns:
            (is_developed: bool, quality_score: float)
        """
        try:
            scores = []

            # 1. POC Drift Check (last 10 candles)
            if len(data) >= 10:
                recent_data = data.tail(10)
                recent_volume_profile = recent_data.groupby(pd.cut(recent_data['close'], bins=20))['volume'].sum()
                recent_poc_idx = recent_volume_profile.idxmax()
                recent_poc = (recent_poc_idx.left + recent_poc_idx.right) / 2
                poc_drift = abs(recent_poc - poc) / poc * 100
                poc_drift_score = 100 if poc_drift < 0.3 else max(0, 100 - (poc_drift - 0.3) * 200)
                scores.append(poc_drift_score)
            else:
                scores.append(50)  # Neutral if not enough data

            # 2. Skewness Check
            skewness = stats.skew(data['close'])
            skewness_score = 100 if abs(skewness) <= 0.25 else max(0, 100 - (abs(skewness) - 0.25) * 200)
            scores.append(skewness_score)

            # 3. Kurtosis Check
            kurtosis = stats.kurtosis(data['close'], fisher=False)  # Pearson's definition
            kurtosis_score = 100 if 2.5 <= kurtosis <= 3.5 else max(0, 100 - abs(kurtosis - 3.0) * 50)
            scores.append(kurtosis_score)

            # 4. Value Area Coverage Check (≥65% within ±1σ)
            va_high = mean + std
            va_low = mean - std
            within_va = ((data['close'] >= va_low) & (data['close'] <= va_high)).sum()
            va_coverage = within_va / len(data) * 100
            va_score = 100 if va_coverage >= 65 else va_coverage * (100/65)
            scores.append(va_score)

            # Calculate overall quality score
            quality_score = sum(scores) / len(scores)

            # Profile is developed if quality score > 70
            is_developed = quality_score >= 70

            return is_developed, quality_score

        except Exception as e:
            cprint(f"⚠️ Error checking development: {e}", "yellow")
            return False, 0

    def calculate_atr(self, df: pd.DataFrame, period: int = 14) -> float:
        """Calculate Average True Range as percentage of price"""
        try:
            high = df['high']
            low = df['low']
            close = df['close']

            # True Range calculation
            tr1 = high - low
            tr2 = abs(high - close.shift())
            tr3 = abs(low - close.shift())

            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean().iloc[-1]

            # Convert to percentage
            current_price = close.iloc[-1]
            atr_percent = (atr / current_price) * 100

            return atr_percent

        except Exception as e:
            cprint(f"⚠️ Error calculating ATR: {e}", "yellow")
            return 0

    def generate_signals(self) -> Optional[Dict]:
        """
        Generate trading signals based on Volume Profile Mean Reversion

        Returns:
            dict: {
                'symbol': str,
                'direction': 'LONG' | 'SHORT' | 'NEUTRAL',
                'confidence': float (0-100),
                'entry_price': float,
                'target_price': float,
                'stop_loss': float,
                'leverage': int (1-20),
                'timeframe': str,
                'volume_profile': dict,
                'reasoning': str,
                'metadata': dict
            }
        """
        try:
            cprint(f"\n{'='*60}", "cyan")
            cprint(f"🔍 Analyzing {self.symbol} on {self.timeframe} timeframe", "cyan")
            cprint(f"{'='*60}", "cyan")

            # Fetch OHLCV data from Hyperliquid
            df = hl.get_ohlcv_data(
                symbol=self.symbol,
                interval=self.timeframe,
                lookback=self.lookback_max + 50  # Extra buffer for calculations
            )

            if df is None or len(df) < self.lookback_max:
                cprint(f"❌ Insufficient data for {self.symbol}", "red")
                return None

            cprint(f"✅ Fetched {len(df)} candles", "green")

            # Calculate ATR
            atr_percent = self.calculate_atr(df)
            cprint(f"📊 ATR: {atr_percent:.3f}%", "cyan")

            # Check ATR volatility window
            if not (self.atr_min <= atr_percent <= self.atr_max):
                cprint(f"⚠️ ATR outside valid range ({self.atr_min}%-{self.atr_max}%)", "yellow")
                return self._neutral_signal("ATR outside optimal range")

            # Try different lookback periods to find developed profile
            best_profile = None
            best_score = 0

            for lookback in range(self.lookback_min, self.lookback_max + 1, 10):
                profile = self.calculate_volume_profile(df, lookback)

                if profile and profile['developed'] and profile['development_score'] > best_score:
                    best_profile = profile
                    best_score = profile['development_score']
                    self.optimal_lookback = lookback

            if best_profile is None:
                cprint(f"⚠️ No developed profile found", "yellow")
                return self._neutral_signal("Volume profile not developed")

            cprint(f"✅ Found developed profile (Score: {best_score:.1f}, Lookback: {self.optimal_lookback})", "green")
            cprint(f"   POC: ${best_profile['poc']:.2f}", "cyan")
            cprint(f"   Value Area: ${best_profile['value_area_low']:.2f} - ${best_profile['value_area_high']:.2f}", "cyan")
            cprint(f"   ±2σ Range: ${best_profile['sigma_2_low']:.2f} - ${best_profile['sigma_2_high']:.2f}", "cyan")

            # Get current and previous candle
            current_candle = df.iloc[-1]
            prev_candle = df.iloc[-2]

            current_price = current_candle['close']
            current_low = current_candle['low']
            current_high = current_candle['high']
            prev_close = prev_candle['close']

            cprint(f"📈 Current Price: ${current_price:.2f}", "cyan")

            # Check for entry conditions
            signal = self._check_entry_conditions(
                current_price=current_price,
                current_low=current_low,
                current_high=current_high,
                prev_close=prev_close,
                profile=best_profile,
                atr_percent=atr_percent
            )

            return signal

        except Exception as e:
            cprint(f"❌ Error generating signals: {e}", "red")
            import traceback
            traceback.print_exc()
            return None

    def _check_entry_conditions(self, current_price: float, current_low: float,
                                current_high: float, prev_close: float,
                                profile: Dict, atr_percent: float) -> Optional[Dict]:
        """Check if entry conditions are met for LONG or SHORT"""

        poc = profile['poc']
        va_high = profile['value_area_high']
        va_low = profile['value_area_low']
        sigma_2_high = profile['sigma_2_high']
        sigma_2_low = profile['sigma_2_low']

        # Check LONG Setup
        # Price touched/wicked below -1σ or -2σ AND current candle closed back inside VA
        if current_low <= va_low:  # Touched -1σ
            if va_low <= current_price <= va_high:  # Closed inside VA

                # Determine entry level
                if current_low <= sigma_2_low:
                    entry_level = "2σ"
                    stop_loss = sigma_2_low - (sigma_2_low * 0.0025)  # 0.25% beyond -2σ
                else:
                    entry_level = "1σ"
                    stop_loss = sigma_2_low - (va_low * 0.0015)  # Just beyond -2σ with buffer

                # Calculate target (0.9x distance to POC)
                distance_to_poc = abs(poc - current_price)
                target_price = current_price + (distance_to_poc * self.tp_fraction)

                # Calculate leverage based on risk/reward
                risk = current_price - stop_loss
                reward = target_price - current_price
                risk_reward = reward / risk if risk > 0 else 0

                # Higher R:R = higher leverage (but cap at 20x)
                leverage = min(20, max(2, int(risk_reward * 3)))

                cprint(f"\n🟢 LONG SETUP DETECTED!", "green", attrs=['bold'])
                cprint(f"   Entry Level: {entry_level}", "green")
                cprint(f"   Entry: ${current_price:.2f}", "green")
                cprint(f"   Target: ${target_price:.2f}", "green")
                cprint(f"   Stop: ${stop_loss:.2f}", "green")
                cprint(f"   R:R: {risk_reward:.2f}", "green")
                cprint(f"   Leverage: {leverage}x", "green")

                return {
                    'symbol': self.symbol,
                    'direction': 'LONG',
                    'confidence': profile['development_score'],
                    'entry_price': current_price,
                    'target_price': target_price,
                    'stop_loss': stop_loss,
                    'leverage': leverage,
                    'timeframe': self.timeframe,
                    'volume_profile': profile,
                    'atr_percent': atr_percent,
                    'risk_reward': risk_reward,
                    'reasoning': f"Price wicked to {entry_level} (${current_low:.2f}) and closed back inside value area at ${current_price:.2f}. POC at ${poc:.2f}. Developed profile score: {profile['development_score']:.1f}. ATR: {atr_percent:.3f}%.",
                    'metadata': {
                        'entry_level': entry_level,
                        'poc': poc,
                        'value_area_high': va_high,
                        'value_area_low': va_low,
                        'lookback': profile['lookback'],
                        'timeout_candles': self.timeout_candles
                    }
                }

        # Check SHORT Setup
        # Price touched/wicked above +1σ or +2σ AND current candle closed back inside VA
        if current_high >= va_high:  # Touched +1σ
            if va_low <= current_price <= va_high:  # Closed inside VA

                # Determine entry level
                if current_high >= sigma_2_high:
                    entry_level = "2σ"
                    stop_loss = sigma_2_high + (sigma_2_high * 0.0025)  # 0.25% beyond +2σ
                else:
                    entry_level = "1σ"
                    stop_loss = sigma_2_high + (va_high * 0.0015)  # Just beyond +2σ with buffer

                # Calculate target (0.9x distance to POC)
                distance_to_poc = abs(current_price - poc)
                target_price = current_price - (distance_to_poc * self.tp_fraction)

                # Calculate leverage based on risk/reward
                risk = stop_loss - current_price
                reward = current_price - target_price
                risk_reward = reward / risk if risk > 0 else 0

                # Higher R:R = higher leverage (but cap at 20x)
                leverage = min(20, max(2, int(risk_reward * 3)))

                cprint(f"\n🔴 SHORT SETUP DETECTED!", "red", attrs=['bold'])
                cprint(f"   Entry Level: {entry_level}", "red")
                cprint(f"   Entry: ${current_price:.2f}", "red")
                cprint(f"   Target: ${target_price:.2f}", "red")
                cprint(f"   Stop: ${stop_loss:.2f}", "red")
                cprint(f"   R:R: {risk_reward:.2f}", "red")
                cprint(f"   Leverage: {leverage}x", "red")

                return {
                    'symbol': self.symbol,
                    'direction': 'SHORT',
                    'confidence': profile['development_score'],
                    'entry_price': current_price,
                    'target_price': target_price,
                    'stop_loss': stop_loss,
                    'leverage': leverage,
                    'timeframe': self.timeframe,
                    'volume_profile': profile,
                    'atr_percent': atr_percent,
                    'risk_reward': risk_reward,
                    'reasoning': f"Price wicked to {entry_level} (${current_high:.2f}) and closed back inside value area at ${current_price:.2f}. POC at ${poc:.2f}. Developed profile score: {profile['development_score']:.1f}. ATR: {atr_percent:.3f}%.",
                    'metadata': {
                        'entry_level': entry_level,
                        'poc': poc,
                        'value_area_high': va_high,
                        'value_area_low': va_low,
                        'lookback': profile['lookback'],
                        'timeout_candles': self.timeout_candles
                    }
                }

        # No setup found
        cprint(f"⚪ No entry conditions met", "white")
        return self._neutral_signal("Waiting for mean reversion setup")

    def _neutral_signal(self, reason: str) -> Dict:
        """Return a neutral signal with reasoning"""
        return {
            'symbol': self.symbol,
            'direction': 'NEUTRAL',
            'confidence': 0,
            'entry_price': 0,
            'target_price': 0,
            'stop_loss': 0,
            'leverage': 1,
            'timeframe': self.timeframe,
            'volume_profile': None,
            'reasoning': reason,
            'metadata': {}
        }


# Test the strategy
if __name__ == "__main__":
    cprint("\n🧪 Volume Profile Strategy Test\n", "cyan", attrs=['bold'])

    # Test with BTC on 1m
    strategy = VolumeProfileStrategy(symbol='BTC', timeframe='1m')
    signal = strategy.generate_signals()

    if signal:
        cprint(f"\n📊 Signal Generated:", "cyan")
        cprint(f"   Symbol: {signal['symbol']}", "cyan")
        cprint(f"   Direction: {signal['direction']}", "cyan")
        cprint(f"   Confidence: {signal['confidence']:.1f}%", "cyan")
        if signal['direction'] != 'NEUTRAL':
            cprint(f"   Entry: ${signal['entry_price']:.2f}", "cyan")
            cprint(f"   Target: ${signal['target_price']:.2f}", "cyan")
            cprint(f"   Stop: ${signal['stop_loss']:.2f}", "cyan")
            cprint(f"   Leverage: {signal['leverage']}x", "cyan")
        cprint(f"   Reasoning: {signal['reasoning']}", "yellow")
    else:
        cprint("\n❌ No signal generated", "red")

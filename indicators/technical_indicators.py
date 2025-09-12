#!/usr/bin/env python3
"""
Technical Indicators Module - Pure Indicator Calculations
Clean, focused, and efficient indicator functions
"""
import pandas as pd
import pandas_ta as ta
import numpy as np
import logging
import math
from typing import Optional, Dict, Any
from bnb.binance import RobotBinance

try:
    import talib
    TALIB_AVAILABLE = True
except ImportError:
    TALIB_AVAILABLE = False

class TechnicalAnalyzer:
    """
    Pure technical analysis class focused only on indicator calculations
    """
    
    def __init__(self, symbol: str, timeframe: str = "1h"):
        """
        Initialize the Technical Analyzer
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            timeframe: Candlestick interval ('1m', '5m', '15m', '1h', '4h', '1d')
        """
        self.symbol = symbol.upper()
        self.timeframe = timeframe
        self.logger = logging.getLogger(f"TechnicalAnalyzer-{self.symbol}")
        self.binance_client = RobotBinance(pair=self.symbol, temporality=self.timeframe)
        self.df = None
        
        self.logger.info(f"🏛️ Spartan Analyzer initialized for {self.symbol} on {self.timeframe}")
    
    def fetch_market_data(self, limit: int = 500) -> pd.DataFrame:
        """
        Fetch real market data from Binance
        
        Args:
            limit: Number of candles to fetch (max 1500)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            self.logger.info(f"⚔️ Fetching {limit} candles for {self.symbol}")
            
            # Get real market data from Binance
            self.df = self.binance_client.candlestick(limit=limit)
            
            if self.df.empty:
                raise ValueError(f"No market data received for {self.symbol}")
            
            self.logger.info(f"✅ Retrieved {len(self.df)} candles from {self.df.index[0]} to {self.df.index[-1]}")
            return self.df
            
        except Exception as e:
            self.logger.error(f"💀 Failed to fetch market data: {str(e)}")
            raise
    
    def calculate_sma(self, period: int = 20, source: str = 'close') -> pd.Series:
        """
        Calculate Simple Moving Average
        
        Args:
            period: SMA period (default 20)
            source: Price source ('open', 'high', 'low', 'close', 'volume')
            
        Returns:
            Series with SMA values
        """
        if self.df is None or self.df.empty:
            raise ValueError("No market data available. Call fetch_market_data() first")
        
        if source not in self.df.columns:
            raise ValueError(f"Invalid source '{source}'. Available: {list(self.df.columns)}")
        
        try:
            sma = ta.sma(self.df[source], length=period)
            self.logger.info(f"📊 SMA({period}) calculated for {source} price")
            return sma
            
        except Exception as e:
            self.logger.error(f"💀 SMA calculation failed: {str(e)}")
            raise
    
    def trend_magic(self, period: int = 20, coeff: float = 1.0, atr_period: int = 5) -> Dict[str, Any]:
        """
        Calculate Trend Magic indicator
        
        Args:
            period: CCI period (default: 20)
            coeff: ATR multiplier (default: 1.0)
            atr_period: ATR period (default: 5)
            
        Returns:
            Dictionary with Trend Magic analysis
        """
        if self.df is None or self.df.empty:
            raise ValueError("No market data available. Call fetch_market_data() first")
        
        try:
            data = self.df.copy()
            
            # Calculate ATR using SMA (as in PineScript)
            data['ATR'] = ta.atr(data['high'], data['low'], data['close'], 
                               length=atr_period, mamode='sma')
            
            # Calculate CCI
            data['CCI'] = ta.cci(data['high'], data['low'], data['close'], 
                               length=period)
            
            # Calculate upper and lower bands
            upT = data['low'] - data['ATR'] * coeff
            downT = data['high'] + data['ATR'] * coeff
            
            # Initialize MagicTrend
            data['MagicTrend'] = 0.0
            
            # Calculate MagicTrend
            for i in range(len(data)):
                if i == 0:
                    if data['CCI'].iloc[i] >= 0:
                        data.loc[data.index[i], 'MagicTrend'] = upT.iloc[i]
                    else:
                        data.loc[data.index[i], 'MagicTrend'] = downT.iloc[i]
                else:
                    if data['CCI'].iloc[i] >= 0:
                        data.loc[data.index[i], 'MagicTrend'] = max(upT.iloc[i], 
                                                                  data['MagicTrend'].iloc[i-1])
                    else:
                        data.loc[data.index[i], 'MagicTrend'] = min(downT.iloc[i], 
                                                                  data['MagicTrend'].iloc[i-1])
            
            # Assign colors based on trend (CCI >= 0)
            data['MagicTrend_Color'] = np.where(data['CCI'] >= 0, 'BLUE', 'RED')
            
            # Detect buy and sell signals
            data['BuySignal'] = False
            data['SellSignal'] = False
            
            for i in range(1, len(data)):
                # Buy signal: when low crosses above MagicTrend
                if (data['low'].iloc[i-1] <= data['MagicTrend'].iloc[i-1] and 
                    data['low'].iloc[i] > data['MagicTrend'].iloc[i]):
                    data.loc[data.index[i], 'BuySignal'] = True
                
                # Sell signal: when high crosses below MagicTrend
                if (data['high'].iloc[i-1] >= data['MagicTrend'].iloc[i-1] and 
                    data['high'].iloc[i] < data['MagicTrend'].iloc[i]):
                    data.loc[data.index[i], 'SellSignal'] = True
            
            # Get current values
            current = data.iloc[-1]
            
            # Determine trend strength
            if current['MagicTrend_Color'] == 'BLUE':
                trend_status = "🔵 BULLISH MAGIC"
                trend_emoji = "🐂"
            else:
                trend_status = "🔴 BEARISH MAGIC"
                trend_emoji = "🐻"
            
            # Calculate distance from trend line
            distance_pct = ((current['close'] - current['MagicTrend']) / current['MagicTrend']) * 100
            
            result = {
                'magic_trend_value': current['MagicTrend'],
                'color': current['MagicTrend_Color'],
                'trend_status': trend_status,
                'trend_emoji': trend_emoji,
                'cci_value': current['CCI'],
                'atr_value': current['ATR'],
                'distance_pct': distance_pct,
                'buy_signal': current['BuySignal'],
                'sell_signal': current['SellSignal'],
                'current_price': current['close']
            }
            
            self.logger.info(f"🔮 Trend Magic calculated: {trend_status}")
            return result
            
        except Exception as e:
            self.logger.error(f"💀 Trend Magic calculation failed: {str(e)}")
            raise
    
    def get_trend_magic_color(self, period: int = 20, coeff: float = 1.0, atr_period: int = 5) -> str:
        """
        Get only the Trend Magic color
        
        Returns:
            'BLUE' for bullish or 'RED' for bearish
        """
        magic_data = self.trend_magic(period, coeff, atr_period)
        return magic_data['color']
    
    def squeeze_momentum(self, bb_length: int = 20, bb_mult: float = 2.0, 
                        kc_length: int = 20, kc_mult: float = 1.5, 
                        use_true_range: bool = True) -> Dict[str, Any]:
        """
        Calculate Squeeze Momentum Indicator by LazyBear
        
        Args:
            bb_length: Bollinger Bands length (default: 20)
            bb_mult: Bollinger Bands multiplier (default: 2.0)
            kc_length: Keltner Channel length (default: 20)
            kc_mult: Keltner Channel multiplier (default: 1.5)
            use_true_range: Use True Range for KC calculation (default: True)
            
        Returns:
            Dictionary with Squeeze Momentum analysis
        """
        if self.df is None or self.df.empty:
            raise ValueError("No market data available. Call fetch_market_data() first")
        
        try:
            data = self.df.copy()
            source = data['close']
            
            # Calculate Bollinger Bands
            basis = ta.sma(source, length=bb_length)
            dev = bb_mult * ta.stdev(source, length=bb_length)
            upper_bb = basis + dev
            lower_bb = basis - dev
            
            # Calculate Keltner Channels
            ma = ta.sma(source, length=kc_length)
            
            if use_true_range:
                # Calculate True Range
                tr_data = ta.true_range(data['high'], data['low'], data['close'])
                range_ma = ta.sma(tr_data, length=kc_length)
            else:
                # Use High - Low
                range_data = data['high'] - data['low']
                range_ma = ta.sma(range_data, length=kc_length)
            
            upper_kc = ma + range_ma * kc_mult
            lower_kc = ma - range_ma * kc_mult
            
            # Squeeze conditions
            sqz_on = (lower_bb > lower_kc) & (upper_bb < upper_kc)
            sqz_off = (lower_bb < lower_kc) & (upper_bb > upper_kc)
            no_sqz = ~sqz_on & ~sqz_off
            
            # Calculate momentum value using linear regression
            # Equivalent to: linreg(source - avg(avg(highest(high, kc_length), lowest(low, kc_length)), sma(close, kc_length)), kc_length, 0)
            
            # Calculate highest and lowest over kc_length periods
            highest_high = data['high'].rolling(window=kc_length).max()
            lowest_low = data['low'].rolling(window=kc_length).min()
            
            # Calculate the average of highest/lowest and sma of close
            avg_hl = (highest_high + lowest_low) / 2
            sma_close = ta.sma(data['close'], length=kc_length)
            avg_base = (avg_hl + sma_close) / 2
            
            # Linear regression of (source - avg_base)
            momentum_source = source - avg_base
            
            # Calculate linear regression manually (equivalent to linreg in PineScript)
            val = pd.Series(index=data.index, dtype=float)
            
            for i in range(kc_length - 1, len(data)):
                y_values = momentum_source.iloc[i - kc_length + 1:i + 1].values
                x_values = np.arange(kc_length)
                
                # Linear regression: y = mx + b, we want the slope (m) * (kc_length - 1) + b
                if len(y_values) == kc_length:
                    slope, intercept = np.polyfit(x_values, y_values, 1)
                    val.iloc[i] = slope * (kc_length - 1) + intercept
            
            # Get current values
            current_val = val.iloc[-1] if not pd.isna(val.iloc[-1]) else 0
            prev_val = val.iloc[-2] if len(val) > 1 and not pd.isna(val.iloc[-2]) else 0
            
            # Determine momentum color (equivalent to bcolor in PineScript)
            if current_val > 0:
                if current_val > prev_val:
                    momentum_color = "LIME"  # Bullish increasing
                else:
                    momentum_color = "GREEN"  # Bullish decreasing
            else:
                if current_val < prev_val:
                    momentum_color = "RED"  # Bearish decreasing
                else:
                    momentum_color = "MAROON"  # Bearish increasing
            
            # Determine squeeze color (equivalent to scolor in PineScript)
            current_sqz_on = sqz_on.iloc[-1] if not pd.isna(sqz_on.iloc[-1]) else False
            current_sqz_off = sqz_off.iloc[-1] if not pd.isna(sqz_off.iloc[-1]) else False
            current_no_sqz = no_sqz.iloc[-1] if not pd.isna(no_sqz.iloc[-1]) else False
            
            if current_no_sqz:
                squeeze_color = "BLUE"  # No squeeze
            elif current_sqz_on:
                squeeze_color = "BLACK"  # Squeeze on
            else:
                squeeze_color = "GRAY"  # Squeeze off
            
            # Determine squeeze status
            if current_sqz_on:
                squeeze_status = "🔴 SQUEEZE ON"
            elif current_sqz_off:
                squeeze_status = "🟢 SQUEEZE OFF"
            else:
                squeeze_status = "🔵 NO SQUEEZE"
            
            # Determine momentum trend
            if momentum_color in ["LIME", "GREEN"]:
                momentum_trend = "🟢 BULLISH"
            else:
                momentum_trend = "🔴 BEARISH"
            
            result = {
                'momentum_value': current_val,
                'momentum_color': momentum_color,
                'momentum_trend': momentum_trend,
                'squeeze_color': squeeze_color,
                'squeeze_status': squeeze_status,
                'squeeze_on': current_sqz_on,
                'squeeze_off': current_sqz_off,
                'no_squeeze': current_no_sqz,
                'bb_upper': upper_bb.iloc[-1],
                'bb_lower': lower_bb.iloc[-1],
                'kc_upper': upper_kc.iloc[-1],
                'kc_lower': lower_kc.iloc[-1],
                'current_price': data['close'].iloc[-1]
            }
            
            self.logger.info(f"🎯 Squeeze Momentum calculated: {squeeze_status} | {momentum_trend}")
            return result
            
        except Exception as e:
            self.logger.error(f"💀 Squeeze Momentum calculation failed: {str(e)}")
            raise
    
    def get_squeeze_status(self, bb_length: int = 20, bb_mult: float = 2.0, 
                          kc_length: int = 20, kc_mult: float = 1.5) -> str:
        """
        Get only the Squeeze status
        
        Returns:
            'SQUEEZE_ON', 'SQUEEZE_OFF', or 'NO_SQUEEZE'
        """
        squeeze_data = self.squeeze_momentum(bb_length, bb_mult, kc_length, kc_mult)
        
        if squeeze_data['squeeze_on']:
            return 'SQUEEZE_ON'
        elif squeeze_data['squeeze_off']:
            return 'SQUEEZE_OFF'
        else:
            return 'NO_SQUEEZE'
    
    def trend_magic_v2(self, period: int = 20, coeff: float = 1.0, atr_period: int = 5) -> Dict[str, Any]:
        """
        Alternative Trend Magic implementation (Version 2)
        Based on your previous working code - for comparison with current version
        
        Args:
            period: CCI period (default: 20)
            coeff: ATR multiplier (default: 1.0)
            atr_period: ATR period (default: 5)
            
        Returns:
            Dictionary with Trend Magic V2 analysis
        """
        if self.df is None or self.df.empty:
            raise ValueError("No market data available. Call fetch_market_data() first")
        
        try:
            data = self.df.copy()
            
            # Calculate CCI using pandas_ta
            cci = ta.cci(data['high'], data['low'], data['close'], length=period)
            
            # Calculate ATR using pandas_ta
            atr = ta.atr(data['high'], data['low'], data['close'], length=atr_period)
            
            # Calculate upper and lower bands
            up = data['low'] - atr * coeff
            down = data['high'] + atr * coeff
            
            # Initialize magic_trend series
            magic_trend = pd.Series([0.0] * len(data), index=data.index)
            
            # Calculate magic trend using your original logic
            for i in range(len(data)):
                # Determine color based on CCI
                current_color = 'BLUE' if cci.iloc[i] > 0 else 'RED'
                
                if cci.iloc[i] >= 0:
                    if not pd.isna(up.iloc[i]):
                        magic_trend.iloc[i] = up.iloc[i] if i == 0 else max(up.iloc[i], magic_trend.iloc[i - 1])
                    else:
                        magic_trend.iloc[i] = magic_trend.iloc[i - 1] if i > 0 else np.nan
                else:
                    if not pd.isna(down.iloc[i]):
                        magic_trend.iloc[i] = down.iloc[i] if i == 0 else min(down.iloc[i], magic_trend.iloc[i - 1])
                    else:
                        magic_trend.iloc[i] = magic_trend.iloc[i - 1] if i > 0 else np.nan
            
            # Get current values
            current_magic_trend = magic_trend.iloc[-1]
            current_cci = cci.iloc[-1]
            current_price = data['close'].iloc[-1]
            
            # Determine current color
            current_color = 'BLUE' if current_cci > 0 else 'RED'
            
            # Determine trend status
            if current_color == 'BLUE':
                trend_status = "🔵 BULLISH MAGIC V2"
                trend_emoji = "🐂"
            else:
                trend_status = "🔴 BEARISH MAGIC V2"
                trend_emoji = "🐻"
            
            # Calculate distance from trend line
            if not pd.isna(current_magic_trend) and current_magic_trend != 0:
                distance_pct = ((current_price - current_magic_trend) / current_magic_trend) * 100
            else:
                distance_pct = 0.0
            
            # Detect signals (simplified version)
            buy_signal = False
            sell_signal = False
            
            if len(data) > 1:
                prev_low = data['low'].iloc[-2]
                prev_magic = magic_trend.iloc[-2]
                current_low = data['low'].iloc[-1]
                
                # Buy signal: low crosses above magic trend
                if prev_low <= prev_magic and current_low > current_magic_trend:
                    buy_signal = True
                
                prev_high = data['high'].iloc[-2]
                current_high = data['high'].iloc[-1]
                
                # Sell signal: high crosses below magic trend
                if prev_high >= prev_magic and current_high < current_magic_trend:
                    sell_signal = True
            
            result = {
                'magic_trend_value': round(current_magic_trend, 3) if not pd.isna(current_magic_trend) else 0.0,
                'color': current_color,
                'trend_status': trend_status,
                'trend_emoji': trend_emoji,
                'cci_value': current_cci,
                'atr_value': atr.iloc[-1],
                'distance_pct': distance_pct,
                'buy_signal': buy_signal,
                'sell_signal': sell_signal,
                'current_price': current_price,
                'version': 'V2'
            }
            
            self.logger.info(f"🔮 Trend Magic V2 calculated: {trend_status}")
            return result
            
        except Exception as e:
            self.logger.error(f"💀 Trend Magic V2 calculation failed: {str(e)}")
            raise
    
    def get_trend_magic_v2_color(self, period: int = 20, coeff: float = 1.0, atr_period: int = 5) -> str:
        """
        Get only the Trend Magic V2 color
        
        Returns:
            'BLUE' for bullish or 'RED' for bearish
        """
        magic_data = self.trend_magic_v2(period, coeff, atr_period)
        return magic_data['color']
    
    def trend_magic_v3(self, period: int = 20, coeff: float = 1.0, atr_period: int = 5) -> Dict[str, Any]:
        """
        Trend Magic V3 - Using TA-Lib directly (your original implementation)
        This version uses TA-Lib exactly as in your original code
        
        Args:
            period: CCI period (default: 20)
            coeff: ATR multiplier (default: 1.0)
            atr_period: ATR period (default: 5)
            
        Returns:
            Dictionary with Trend Magic V3 analysis
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is required for trend_magic_v3. Install with: pip install TA-Lib")
        
        if self.df is None or self.df.empty:
            raise ValueError("No market data available. Call fetch_market_data() first")
        
        try:
            data = self.df.copy()
            
            # Extract OHLC arrays for TA-Lib
            high = data['high'].values
            low = data['low'].values
            close = data['close'].values
            
            # Calculate CCI using TA-Lib (exactly as in your original code)
            cci = talib.CCI(high, low, close, timeperiod=period)
            
            # Calculate ATR using TA-Lib
            atr = talib.ATR(high, low, close, timeperiod=atr_period)
            
            # Calculate upper and lower bands
            up = low - atr * coeff
            down = high + atr * coeff
            
            # Initialize magic_trend series (exactly as in your original code)
            magic_trend = pd.Series([0.0] * len(data), index=data.index)
            
            # Calculate magic trend using your exact original logic
            for i in range(len(data)):
                # Define color based on CCI (exactly as in your original code)
                current_color = 'BLUE' if cci[i] > 0 else 'RED'
                
                if cci[i] >= 0:
                    if not math.isnan(up[i]):
                        magic_trend.iloc[i] = up[i] if i == 0 else max(up[i], magic_trend.iloc[i - 1])
                    else:
                        magic_trend.iloc[i] = magic_trend.iloc[i - 1] if i > 0 else np.nan
                else:
                    if not math.isnan(down[i]):
                        magic_trend.iloc[i] = down[i] if i == 0 else min(down[i], magic_trend.iloc[i - 1])
                    else:
                        magic_trend.iloc[i] = magic_trend.iloc[i - 1] if i > 0 else np.nan
            
            # Get current values (exactly as in your original code)
            current_magic_trend = magic_trend.iloc[-1]
            current_cci = cci[-1]
            current_price = close[-1]
            
            # Determine current color
            current_color = 'BLUE' if current_cci > 0 else 'RED'
            
            # Determine trend status
            if current_color == 'BLUE':
                trend_status = "🔵 BULLISH MAGIC V3"
                trend_emoji = "🐂"
            else:
                trend_status = "🔴 BEARISH MAGIC V3"
                trend_emoji = "🐻"
            
            # Calculate distance from trend line
            if not math.isnan(current_magic_trend) and current_magic_trend != 0:
                distance_pct = ((current_price - current_magic_trend) / current_magic_trend) * 100
            else:
                distance_pct = 0.0
            
            # Detect signals (simplified version)
            buy_signal = False
            sell_signal = False
            
            if len(data) > 1:
                prev_low = low[-2]
                prev_magic = magic_trend.iloc[-2]
                current_low = low[-1]
                
                # Buy signal: low crosses above magic trend
                if prev_low <= prev_magic and current_low > current_magic_trend:
                    buy_signal = True
                
                prev_high = high[-2]
                current_high = high[-1]
                
                # Sell signal: high crosses below magic trend
                if prev_high >= prev_magic and current_high < current_magic_trend:
                    sell_signal = True
            
            # Return exactly as in your original code format
            result = {
                'magic_trend_value': round(current_magic_trend, 3) if not math.isnan(current_magic_trend) else 0.0,
                'color': current_color,
                'trend_status': trend_status,
                'trend_emoji': trend_emoji,
                'cci_value': current_cci,
                'atr_value': atr[-1],
                'distance_pct': distance_pct,
                'buy_signal': buy_signal,
                'sell_signal': sell_signal,
                'current_price': current_price,
                'version': 'V3_TALIB'
            }
            
            self.logger.info(f"🔮 Trend Magic V3 (TA-Lib) calculated: {trend_status}")
            return result
            
        except Exception as e:
            self.logger.error(f"💀 Trend Magic V3 calculation failed: {str(e)}")
            raise
    
    def get_trend_magic_v3_color(self, period: int = 20, coeff: float = 1.0, atr_period: int = 5) -> str:
        """
        Get only the Trend Magic V3 color (TA-Lib version)
        
        Returns:
            'BLUE' for bullish or 'RED' for bearish
        """
        if not TALIB_AVAILABLE:
            raise ImportError("TA-Lib is required for trend_magic_v3")
        
        magic_data = self.trend_magic_v3(period, coeff, atr_period)
        return magic_data['color']

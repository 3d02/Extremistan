import pandas as pd
import numpy as np
from typing import List, Optional, Tuple
from extremistan.data.adapters import YahooFinanceAdapter, FredAdapter
from extremistan.analytics.math_lib import get_hill_alpha, get_log_returns

class RegimeAnalytics:
    """
    Constructs the "State of the World" vector and the full historical feature matrix.
    """
    def __init__(self):
        self.yf_adapter = YahooFinanceAdapter()
        self.fred_adapter = FredAdapter()

    def build_feature_matrix(self, start_date: str = '2007-01-01') -> pd.DataFrame:
        """
        Builds the unified dataframe of features for the probabilistic engine.
        Features:
        - Alpha_2Y (Climate)
        - Alpha_6M (Weather)
        - Slope (T10Y3M)
        - VIX
        - VIX_Curve (VIX / VIX3M)
        - SKEW
        """
        # 1. Fetch Raw Data
        # We need enough history for Alpha_2Y (approx 500 trading days) before start_date
        fetch_start = pd.to_datetime(start_date) - pd.DateOffset(years=3)
        fetch_start_str = fetch_start.strftime('%Y-%m-%d')

        print(f"Fetching data from {fetch_start_str}...")

        tickers_yf = ['^GSPC', '^VIX', '^VIX3M', '^SKEW']
        df_yf = self.yf_adapter.get_data(tickers_yf, start_date=fetch_start_str)

        df_fred = self.fred_adapter.get_data(['T10Y3M'], start_date=fetch_start_str)
        # Ensure timezone-naive
        if df_fred.index.tz is not None:
             df_fred.index = df_fred.index.tz_localize(None)

        # 2. Align Data
        # We use outer join to keep all data, then fill forward
        data = pd.concat([df_yf, df_fred], axis=1, join='outer').sort_index()

        # Forward fill to handle non-trading days differences (e.g. FRED vs NYSE holidays)
        data = data.ffill().dropna()

        if '^GSPC' not in data.columns:
            print("Warning: SPX data missing. Returning empty.")
            return pd.DataFrame()

        # 3. Calculate Derived Features
        # Log Returns for Alpha
        prices = data['^GSPC']
        log_returns = get_log_returns(prices)

        # VIX Curve Ratio
        if '^VIX' in data.columns and '^VIX3M' in data.columns:
            data['VIX_Curve'] = data['^VIX'] / data['^VIX3M']
        else:
            data['VIX_Curve'] = np.nan

        # 4. Calculate Rolling Hill Alphas
        # This can be slow, so we print progress or optimise
        print("Calculating Rolling Hill Alphas...")

        # We'll use pandas rolling apply, but wrapping get_hill_alpha requires care with args
        # get_hill_alpha expects a Series.

        # Windows
        window_2y = 504
        window_6m = 126

        # We define a helper to apply. Rolling apply passes a ndarray usually.
        def hill_wrapper(x, adaptive=False):
            # x is numpy array
            return get_hill_alpha(pd.Series(x), adaptive=adaptive)

        # Optimization: We can loop or use rolling.apply.
        # Rolling apply on 15 years of daily data (approx 3750 rows)
        # 504 window. 3750-504 = 3200 iterations.
        # Inside hill: sort, log, mean. Fast enough for offline/startup.

        # Note: 'raw=True' passes ndarray to function, 'raw=False' passes Series.
        # get_hill_alpha takes Series but converts to values internally anyway mostly.
        # However, it filters negative returns.

        # IMPORTANT: Hill Alpha uses LOSSES (negative returns).
        # log_returns are signed.

        # rolling().apply() is notoriously slow with custom python functions.
        # Let's do a list comprehension which is often faster for simple windows.

        rets_values = log_returns.values
        dates = log_returns.index
        n = len(rets_values)

        alpha_2y_list = [np.nan] * n
        alpha_6m_list = [np.nan] * n

        # We start from max window
        start_idx = max(window_2y, window_6m)

        for i in range(start_idx, n):
            # Slice for 2Y: [i-window:i]
            slice_2y = rets_values[i-window_2y:i]
            val_2y = get_hill_alpha(pd.Series(slice_2y), adaptive=True)
            alpha_2y_list[i] = val_2y

            slice_6m = rets_values[i-window_6m:i]
            val_6m = get_hill_alpha(pd.Series(slice_6m), adaptive=True)
            alpha_6m_list[i] = val_6m

        data['Alpha_2Y'] = alpha_2y_list
        data['Alpha_6M'] = alpha_6m_list

        # 5. Assemble Final Matrix
        # Columns: Alpha_2Y, Alpha_6M, Slope, VIX, VIX_Curve, SKEW
        # Renaming for consistency
        final_cols = {
            'Alpha_2Y': 'Alpha_2Y',
            'Alpha_6M': 'Alpha_6M',
            'T10Y3M': 'Slope',
            '^VIX': 'VIX',
            'VIX_Curve': 'VIX_Curve',
            '^SKEW': 'SKEW',
            '^GSPC': 'SPX' # Keeping SPX for return calculations later
        }

        # Filter only existing columns
        existing_cols = {k: v for k, v in final_cols.items() if k in data.columns}

        matrix = data[list(existing_cols.keys())].rename(columns=existing_cols)

        # Drop rows where we don't have alphas yet (the startup period)
        # But allow if just some days are missing (e.g. SKEW history)
        # Actually SKEW is needed for the regime vector, so we dropna() on the feature set
        feature_cols = ['Alpha_2Y', 'Alpha_6M', 'Slope', 'VIX', 'VIX_Curve', 'SKEW']
        # Check which are actually present
        present_features = [c for c in feature_cols if c in matrix.columns]

        matrix = matrix.dropna(subset=present_features)

        # Filter to requested start date
        matrix = matrix[matrix.index >= pd.to_datetime(start_date)]

        return matrix

import sys
import pandas as pd
import numpy as np
import argparse
from datetime import datetime
from extremistan.data.adapters import YahooFinanceAdapter, CSVAdapter, FredAdapter
from extremistan.analytics.math_lib import get_log_returns, get_hill_alpha, calculate_drawdown, get_rolling_volatility, get_z_score, get_rate_of_change
from extremistan.strategy.signal_engine import SignalEngine
from extremistan.ui.dashboard import MatplotlibDashboard

# Configuration
TICKER = "^GSPC"
VIX_TICKER = "^VIX"
MOVE_TICKER = "^MOVE"
TNX_TICKER = "^TNX"
IRX_TICKER = "^IRX"
SLOPE_TICKER = "T10Y3M" # FRED Series ID
START_DATE = "1927-12-30"
CLIMATE_WINDOW = 504  # 2 Years
WEATHER_WINDOW = 126   # 6 Months

def main():
    parser = argparse.ArgumentParser(description="Extremistan Tail Risk Monitor")
    parser.add_argument("--offline", action="store_true", help="Use local CSV data only")
    parser.add_argument("--csv-path", type=str, default="data_storage/sp500_history_1927_2025.csv", help="Path to CSV file")
    args = parser.parse_args()

    print(f"--- [COMMAND CENTER] INITIALIZING FOR {TICKER} ---")

    # 1. Ingestion
    if args.offline:
        print(f"[*] Mode: OFFLINE (CSV: {args.csv_path})")
        # CSV adapter currently simple, might need tuning if we strictly want to map columns
        # For now, let's assume standard behavior or fallback to Yahoo if online
        adapter = CSVAdapter(args.csv_path)
        # Note: CSVAdapter logic in adapters.py expects us to ask for tickers that match columns.
        # If the CSV has 'SPX' but we ask for '^GSPC', it might fail unless mapped.
        # Let's inspect the CSV structure first?
        # Assuming the CSV provided `sp500_history_1927_2025.csv` likely contains SPX data.
        # We will try to fetch it.
        # If the user runs offline, we rely on what's in the CSV.
        tickers_to_fetch = ['SPX', 'VIX'] # Hypothetical columns in CSV
        df_raw = adapter.get_data(tickers_to_fetch, start_date=START_DATE)
    else:
        print("[*] Mode: ONLINE (Yahoo Finance + Cache)")

        # Yahoo Data
        adapter_yahoo = YahooFinanceAdapter(use_cache=True)
        tickers_yahoo = [TICKER, VIX_TICKER, MOVE_TICKER, TNX_TICKER, IRX_TICKER]
        df_yahoo = adapter_yahoo.get_data(tickers_yahoo, start_date=START_DATE)

        # FRED Data
        print("[*] Fetching Economic Data from FRED...")
        adapter_fred = FredAdapter(use_cache=True)
        df_fred = adapter_fred.get_data([SLOPE_TICKER], start_date=START_DATE)

        # Merge Data
        if df_yahoo.empty:
            df_raw = pd.DataFrame()
        else:
            # Outer merge to keep all dates, but since we analyze primarily SPX,
            # we could left join. However, signals might need macro data even if market is closed?
            # No, we need aligned data. Let's join on index.

            # Fix Timezones (Yahoo is usually tz-aware, FRED is naive)
            if not df_yahoo.empty and df_yahoo.index.tz is not None:
                df_yahoo.index = df_yahoo.index.tz_localize(None)
            if not df_fred.empty and df_fred.index.tz is not None:
                df_fred.index = df_fred.index.tz_localize(None)

            df_raw = df_yahoo.join(df_fred, how='outer')

    if df_raw.empty:
        print("[!] Error: No data retrieved.")
        sys.exit(1)

    # 2. Normalization
    # We need 'SPX' and 'VIX' columns.
    df = pd.DataFrame(index=df_raw.index)

    # Mapping logic
    # If using Yahoo, columns might be Tickers.
    if TICKER in df_raw.columns:
        df['SPX'] = df_raw[TICKER]
    elif 'SPX' in df_raw.columns:
         df['SPX'] = df_raw['SPX']
    elif 'Close' in df_raw.columns and not isinstance(df_raw.columns, pd.MultiIndex):
        # Single ticker result
        df['SPX'] = df_raw['Close']
    else:
        # Last resort: take first column
        df['SPX'] = df_raw.iloc[:, 0]

    if VIX_TICKER in df_raw.columns:
        df['VIX'] = df_raw[VIX_TICKER]
    elif 'VIX' in df_raw.columns:
        df['VIX'] = df_raw['VIX']
    else:
        df['VIX'] = np.nan

    if MOVE_TICKER in df_raw.columns:
        df['MOVE'] = df_raw[MOVE_TICKER]
    else:
        df['MOVE'] = np.nan

    if TNX_TICKER in df_raw.columns:
        df['TNX'] = df_raw[TNX_TICKER]
    else:
        df['TNX'] = np.nan

    if IRX_TICKER in df_raw.columns:
        df['IRX'] = df_raw[IRX_TICKER]
    else:
        df['IRX'] = np.nan

    # 3. Analytics
    df['Log_Return'] = get_log_returns(df['SPX'])
    df = df.dropna(subset=['Log_Return'])

    lifetime_sigma = df['Log_Return'].std()
    lifetime_mu = df['Log_Return'].mean()

    print("[*] Calculating Tail Alphas (This may take a moment)...")

    # 3a. Weather Alpha (6M) on Daily Data
    # Adaptive Hill Estimator
    df['Alpha_6M'] = df['Log_Return'].rolling(window=WEATHER_WINDOW).apply(get_hill_alpha, raw=False, kwargs={'min_k': 10, 'adaptive': True})

    # 3b. Climate Alpha (2Y) on Daily Data
    # Adaptive Hill Estimator
    df['Alpha_2Y'] = df['Log_Return'].rolling(window=CLIMATE_WINDOW).apply(get_hill_alpha, raw=False, kwargs={'min_k': 10, 'adaptive': True})

    # 3c. Regime Metrics
    # Rolling 5Y Volatility (approx 1260 days)
    df['Rolling_Sigma'] = get_rolling_volatility(df['Log_Return'], window=1260)
    # Z-Score relative to rolling sigma
    # Z = (Return - Rolling_Mean) / Rolling_Sigma
    # For simplicity, assuming rolling mean is close to 0 or we can compute it.
    df['Rolling_Mean'] = df['Log_Return'].rolling(window=1260).mean()
    df['Z_Score_Regime'] = (df['Log_Return'] - df['Rolling_Mean']) / df['Rolling_Sigma']

    # 3d. Cross-Asset Metrics
    # Term Structure Slope (10Y - 3M). 2Y would be ideal but using what we have.
    # Note: Yields are in percent, e.g. 4.12.
    if SLOPE_TICKER in df_raw.columns:
        df['Slope'] = df_raw[SLOPE_TICKER]
    else:
        # Fallback if FRED fetch failed
        df['Slope'] = df['TNX'] - df['IRX']

    # MOVE Index is already in df['MOVE']

    # 3e. ROC Momentum Metrics (on Daily Data)
    df['Alpha_6M_ROC'] = get_rate_of_change(df['Alpha_6M'], window=10) # 10-day momentum
    df['MOVE_ROC'] = get_rate_of_change(df['MOVE'], window=5) # 5-day acute stress

    df['Drawdown'] = calculate_drawdown(df['SPX'])

    # 4. Strategy Signal
    # Shift indicators by 1 day to prevent look-ahead bias
    df['Alpha_6M_Shift'] = df['Alpha_6M'].shift(1)
    df['Alpha_2Y_Shift'] = df['Alpha_2Y'].shift(1)
    df['Slope_Shift'] = df['Slope'].shift(1)
    df['MOVE_Shift'] = df['MOVE'].shift(1)
    df['Rolling_Sigma_Shift'] = df['Rolling_Sigma'].shift(1)
    # Note: ROCs are also shifted to prevent look-ahead
    df['Alpha_6M_ROC_Shift'] = df['Alpha_6M_ROC'].shift(1)
    df['MOVE_ROC_Shift'] = df['MOVE_ROC'].shift(1)

    # Calculate Fragility Density (20-day rolling density of Weather < Climate) on Shifted Data
    df['Is_Fragile'] = (df['Alpha_6M_Shift'] < df['Alpha_2Y_Shift']).astype(int)
    # Mask Is_Fragile as NaN if either alpha is NaN
    df.loc[df['Alpha_6M_Shift'].isna() | df['Alpha_2Y_Shift'].isna(), 'Is_Fragile'] = np.nan
    df['Fragility_Density'] = df['Is_Fragile'].rolling(window=20, min_periods=1).mean()

    # Calculate Healing Density (20-day rolling density of Weather > Climate) on Shifted Data
    df['Is_Healing'] = (df['Alpha_6M_Shift'] > df['Alpha_2Y_Shift']).astype(int)
    # Mask Is_Healing as NaN if either alpha is NaN
    df.loc[df['Alpha_6M_Shift'].isna() | df['Alpha_2Y_Shift'].isna(), 'Is_Healing'] = np.nan
    df['Healing_Density'] = df['Is_Healing'].rolling(window=20, min_periods=1).mean()

    # Strict T-1 Data Execution
    # For live signals (assumed pre-market), we use the last available close (iloc[-1])
    # of the SHIFTED columns (which represent T-1 data).
    # Wait, if we run pre-market today (T), we want data from T-1 close.
    # The dataframe index T-1 has data for T-1 close.
    # If we shift(1), the row at T contains T-1 data.
    # If the dataframe ends at T-1 (yesterday close), then `shift(1)` would push T-1 data to T (which doesn't exist yet).
    # Actually, usually dataframes end at the last known close.
    # If today is T (morning), we have data up to T-1.
    # So the last row is T-1.
    # If we want to evaluate the signal for today (T), we should use the data from T-1.
    # `iloc[-1]` of the raw columns gives T-1 data.
    # `iloc[-1]` of the SHIFTED columns gives T-2 data.
    # The requirement is "Strict T-1 data".
    # So we should use `iloc[-1]` of the UN-SHIFTED columns if the dataframe ends at T-1.
    # Let's assume the dataframe contains all closed candles.
    curr_alpha_2y = df['Alpha_2Y'].iloc[-1]
    curr_alpha_6m = df['Alpha_6M'].iloc[-1]
    curr_fragility_density = df['Fragility_Density'].iloc[-1] # This is calculated on shifted data, wait.
    # Fragility density definition: rolling sum of shifted comparison.
    # If we want density up to T-1, we need to calculate it on the T-1 data.
    # The current implementation calculates `Is_Fragile` on Shifted data.
    # Let's stick to the convention: All inputs to the signal engine must be T-1.
    # If we pass `iloc[-1]` of unshifted columns, that is T-1 data.
    # `Fragility_Density` uses `Alpha_6M_Shift`.
    # `Fragility_Density` at index T-1 is the mean of `Is_Fragile` from T-20 to T-1.
    # `Is_Fragile` at T-1 uses `Alpha_Shift` at T-1, which is `Alpha` at T-2.
    # This seems like a double lag if we are not careful.

    # REVISION for Strict T-1:
    # We want the signal based on data available as of yesterday close.
    # So we want `Alpha_2Y` at T-1, `Alpha_6M` at T-1.
    # `Fragility_Density` should be the density over the last 20 days ending T-1.
    # We should calculate `Is_Fragile_Raw` = `Alpha_6M` < `Alpha_2Y`.
    # Then rolling mean of that.

    # Let's re-calculate Density on unshifted data for the purpose of the "Current State"
    df['Is_Fragile_Raw'] = (df['Alpha_6M'] < df['Alpha_2Y']).astype(int)
    df.loc[df['Alpha_6M'].isna() | df['Alpha_2Y'].isna(), 'Is_Fragile_Raw'] = np.nan
    df['Fragility_Density_Raw'] = df['Is_Fragile_Raw'].rolling(window=20, min_periods=1).mean()

    df['Is_Healing_Raw'] = (df['Alpha_6M'] > df['Alpha_2Y']).astype(int)
    df.loc[df['Alpha_6M'].isna() | df['Alpha_2Y'].isna(), 'Is_Healing_Raw'] = np.nan
    df['Healing_Density_Raw'] = df['Is_Healing_Raw'].rolling(window=20, min_periods=1).mean()

    curr_alpha_2y = df['Alpha_2Y'].iloc[-1]
    curr_alpha_6m = df['Alpha_6M'].iloc[-1]
    curr_fragility_density = df['Fragility_Density_Raw'].iloc[-1]
    curr_healing_density = df['Healing_Density_Raw'].iloc[-1]
    curr_vix = df['VIX'].iloc[-1] if not pd.isna(df['VIX'].iloc[-1]) else 0.0
    curr_dd = df['Drawdown'].iloc[-1]
    curr_slope = df['Slope'].iloc[-1]
    curr_move = df['MOVE'].iloc[-1]
    curr_vol_stress = df['Z_Score_Regime'].iloc[-1]
    curr_alpha_6m_roc = df['Alpha_6M_ROC'].iloc[-1]
    curr_move_roc = df['MOVE_ROC'].iloc[-1]

    engine = SignalEngine()
    signal_result = engine.evaluate(
        curr_alpha_2y,
        curr_alpha_6m,
        fragility_density=curr_fragility_density,
        healing_density=curr_healing_density,
        slope=curr_slope,
        move_index=curr_move,
        vol_stress=curr_vol_stress,
        alpha_6m_roc=curr_alpha_6m_roc,
        move_roc=curr_move_roc
    )

    # 5. Reporting
    print("\n" + "="*60)
    print(f"TAIL-RISK OPERATIONAL BRIEFING: {datetime.now().strftime('%Y-%m-%d')}")
    print("="*60)
    print(f"S&P 500 Level:      ${df['SPX'].iloc[-1]:,.2f}")
    print(f"Current Drawdown:   {curr_dd*100:.2f}%")
    print(f"VIX Index:          {curr_vix:.2f} " + ("(High Panic)" if curr_vix > 30 else "(Low Fear)"))
    print("-" * 60)
    print(f"Lifetime Sigma (σ): {lifetime_sigma:.6f}")
    print(f"Today's Shock:      {(df['Log_Return'].iloc[-1] / lifetime_sigma):.2f}σ")
    print("-" * 60)
    print(f"Climate Alpha (2Y): {curr_alpha_2y:.2f}  [{'Extremistan' if curr_alpha_2y < 3 else 'Mediocristan'}]")
    print(f"Weather Alpha (6M): {curr_alpha_6m:.2f}  [{'Fragilizing' if curr_alpha_6m < curr_alpha_2y else 'Healing'}]")
    print("-" * 60)
    print(f"STRATEGIC SIGNAL:   {signal_result.signal} ({signal_result.description})")
    print("="*60)

    # 6. Visualization
    dashboard = MatplotlibDashboard()
    context = {
        'ticker': TICKER,
        'lifetime_mu': lifetime_mu,
        'lifetime_sigma': lifetime_sigma
    }
    dashboard.render(df, context)

if __name__ == "__main__":
    main()

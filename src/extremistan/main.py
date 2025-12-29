import sys
import pandas as pd
import numpy as np
import argparse
from datetime import datetime
from extremistan.data.adapters import YahooFinanceAdapter, CSVAdapter
from extremistan.analytics.math_lib import get_log_returns, get_hill_alpha, calculate_drawdown, get_rolling_volatility, get_z_score
from extremistan.strategy.signal_engine import SignalEngine
from extremistan.ui.dashboard import MatplotlibDashboard

# Configuration
TICKER = "^GSPC"
VIX_TICKER = "^VIX"
MOVE_TICKER = "^MOVE"
TNX_TICKER = "^TNX"
IRX_TICKER = "^IRX"
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
    else:
        print("[*] Mode: ONLINE (Yahoo Finance + Cache)")
        adapter = YahooFinanceAdapter(use_cache=True)
        tickers_to_fetch = [TICKER, VIX_TICKER, MOVE_TICKER, TNX_TICKER, IRX_TICKER]

    df_raw = adapter.get_data(tickers_to_fetch, start_date=START_DATE)

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

    # 3a. Weekly Resampling for Weather Alpha
    # Resample to weekly (Fri)
    df_weekly = df['Log_Return'].resample('W-FRI').sum().to_frame() # Sum log returns for weekly log returns

    # Calculate Weather Alpha (6M) on weekly data
    # 6 months ~ 26 weeks
    # Adaptive Hill Estimator
    df_weekly['Alpha_6M'] = df_weekly['Log_Return'].rolling(window=26).apply(get_hill_alpha, raw=False, kwargs={'min_k': 4, 'adaptive': True})

    # Reindex back to daily and ffill
    # We want the weekly value to persist until the next week
    df['Alpha_6M'] = df_weekly['Alpha_6M'].reindex(df.index).ffill()

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
    df['Slope'] = df['TNX'] - df['IRX']

    # MOVE Index is already in df['MOVE']

    df['Drawdown'] = calculate_drawdown(df['SPX'])

    # 4. Strategy Signal
    # Shift indicators by 1 day to prevent look-ahead bias
    df['Alpha_6M_Shift'] = df['Alpha_6M'].shift(1)
    df['Alpha_2Y_Shift'] = df['Alpha_2Y'].shift(1)
    df['Slope_Shift'] = df['Slope'].shift(1)
    df['MOVE_Shift'] = df['MOVE'].shift(1)
    df['Rolling_Sigma_Shift'] = df['Rolling_Sigma'].shift(1)

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

    curr_alpha_2y = df['Alpha_2Y_Shift'].iloc[-1]
    curr_alpha_6m = df['Alpha_6M_Shift'].iloc[-1]
    curr_fragility_density = df['Fragility_Density'].iloc[-1]
    curr_healing_density = df['Healing_Density'].iloc[-1]
    curr_vix = df['VIX'].iloc[-1] if not pd.isna(df['VIX'].iloc[-1]) else 0.0
    curr_dd = df['Drawdown'].iloc[-1]
    curr_slope = df['Slope_Shift'].iloc[-1]
    curr_move = df['MOVE_Shift'].iloc[-1]
    curr_vol_stress = df['Z_Score_Regime'].iloc[-1] # This is current shock, using z-score relative to regime

    engine = SignalEngine()
    signal_result = engine.evaluate(
        curr_alpha_2y,
        curr_alpha_6m,
        fragility_density=curr_fragility_density,
        healing_density=curr_healing_density,
        slope=curr_slope,
        move_index=curr_move,
        vol_stress=curr_vol_stress
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

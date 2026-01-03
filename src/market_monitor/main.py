import sys
import pandas as pd
import numpy as np
import argparse
from datetime import datetime, timedelta
from market_monitor.data.adapters import YahooFinanceAdapter, CSVAdapter, FredAdapter
from market_monitor.data.store import ParquetStore
from market_monitor.analytics.math_lib import get_log_returns, calculate_drawdown
from market_monitor.ui.dashboard import MatplotlibDashboard

# Configuration
TICKER_SPX = "^GSPC"
TICKER_VIX = "^VIX"
TICKER_SLOPE = "T10Y3M" # FRED Series ID
DEFAULT_START_DATE = "1927-12-30"

def fetch_and_update(ticker: str, adapter, store: ParquetStore, start_date_default: str):
    """
    Fetches data for a ticker using delta logic:
    1. Load existing data.
    2. Determine start date (Last Date + 1 or Default).
    3. Fetch new data.
    4. Merge and Save.
    5. Return full dataframe.
    """
    print(f"[*] Processing {ticker}...")

    # 1. Load Existing
    df_existing = store.load(ticker)

    start_date = start_date_default
    if df_existing is not None and not df_existing.empty:
        last_date = df_existing.index[-1]
        # Start from next day
        start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
        # print(f"    - Found existing data up to {last_date.strftime('%Y-%m-%d')}. Fetching delta from {start_date}...")
    else:
        # print(f"    - No existing data. Fetching full history from {start_date}...")
        df_existing = pd.DataFrame()

    # 2. Fetch New (if needed)
    # Check if start_date is in the future
    if pd.to_datetime(start_date) > datetime.now():
        # print("    - Data is up to date.")
        return df_existing

    try:
        # Adapter expects list of tickers
        df_new = adapter.get_data([ticker], start_date=start_date)
    except Exception as e:
        print(f"[!] Error fetching {ticker}: {e}")
        df_new = pd.DataFrame()

    # 3. Merge
    if df_new.empty:
        return df_existing

    # Standardize Column Name (We want a single Series mainly, or standardized DataFrame)
    # The adapter returns a DataFrame, potentially with the ticker as column or 'Close'
    # We want to normalize this BEFORE saving to store to keep store clean?
    # Or keep store raw? The requirement is "cache everything".
    # Let's keep the structure returned by adapter but ensure index alignment.

    if df_existing.empty:
        df_final = df_new
    else:
        # Concatenate
        df_final = pd.concat([df_existing, df_new])

    # Deduplicate
    df_final = df_final[~df_final.index.duplicated(keep='last')]

    # 4. Save
    store.save(df_final, ticker)

    return df_final

def main():
    parser = argparse.ArgumentParser(description="Market Monitor")
    parser.add_argument("--offline", action="store_true", help="Use local data only, do not fetch new data")
    parser.add_argument("--csv-path", type=str, help="Path to CSV file (Legacy/Override)")
    args = parser.parse_args()

    print(f"--- [MARKET MONITOR] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

    store = ParquetStore()

    # Adapters
    # Note: YahooAdapter and FredAdapter currently have their own internal caching in the original code.
    # We should bypass that or rely on our new Store logic.
    # The `adapters.py` logic uses `ParquetStore` but with the old hashing key.
    # We will instantiate them with `use_cache=False` because WE are handling the caching/delta logic here in main.
    adapter_yahoo = YahooFinanceAdapter(use_cache=False)
    adapter_fred = FredAdapter(use_cache=False)

    # 1. Ingestion & Delta Update
    if args.offline:
        print("[*] Mode: OFFLINE")
        df_spx = store.load(TICKER_SPX)
        df_vix = store.load(TICKER_VIX)
        df_slope = store.load(TICKER_SLOPE)
    else:
        print("[*] Mode: ONLINE (Delta Sync)")
        df_spx = fetch_and_update(TICKER_SPX, adapter_yahoo, store, DEFAULT_START_DATE)
        df_vix = fetch_and_update(TICKER_VIX, adapter_yahoo, store, "1990-01-01") # VIX usually starts 1990
        df_slope = fetch_and_update(TICKER_SLOPE, adapter_fred, store, DEFAULT_START_DATE)

    if df_spx is None or df_spx.empty:
        print("[!] Error: No SPX data available.")
        sys.exit(1)

    # 2. Normalization & Alignment
    # We need a master dataframe aligned to SPX trading days
    df = pd.DataFrame(index=df_spx.index)

    # Extract Series.
    # Yahoo adapter result structure varies (MultiIndex or not).
    def extract_series(df_in, col_name_candidate):
        if df_in is None or df_in.empty: return pd.Series(dtype=float)
        # If MultiIndex columns (Ticker, Attribute)
        if isinstance(df_in.columns, pd.MultiIndex):
            # Try to find 'Close' for the ticker
            try:
                return df_in['Close'][col_name_candidate]
            except KeyError:
                # Maybe just one level?
                pass

        # If simple index
        if col_name_candidate in df_in.columns:
            return df_in[col_name_candidate]
        elif 'Close' in df_in.columns:
            return df_in['Close']
        elif 'SPX' in df_in.columns: # Legacy CSV
            return df_in['SPX']
        elif 'VIX' in df_in.columns:
            return df_in['VIX']
        elif 'T10Y3M' in df_in.columns:
            return df_in['T10Y3M']
        else:
            return df_in.iloc[:, 0]

    df['SPX'] = extract_series(df_spx, TICKER_SPX)

    # Join VIX and Slope (forward fill for days when macro data is missing but market is open?)
    # Usually we want to align to SPX index.
    s_vix = extract_series(df_vix, TICKER_VIX)
    s_slope = extract_series(df_slope, TICKER_SLOPE)

    # Reindex to match SPX
    df['VIX'] = s_vix.reindex(df.index, method='ffill')
    df['Slope'] = s_slope.reindex(df.index, method='ffill')

    # 3. Analytics
    df['Log_Return'] = get_log_returns(df['SPX'])
    df['Drawdown'] = calculate_drawdown(df['SPX'])

    # Drop first NaN from log return
    df = df.dropna(subset=['Log_Return'])

    # Lifetime Metrics
    lifetime_sigma = df['Log_Return'].std()
    lifetime_mad = (df['Log_Return'] - df['Log_Return'].mean()).abs().mean()

    current_log_ret = df['Log_Return'].iloc[-1]
    current_sigma_move = current_log_ret / lifetime_sigma
    current_mad_move = current_log_ret / lifetime_mad

    # 4. Reporting
    print("\n" + "="*60)
    print(f"MARKET MONITOR REPORT: {df.index[-1].strftime('%Y-%m-%d')}")
    print("="*60)
    print(f"S&P 500 Level:      ${df['SPX'].iloc[-1]:,.2f}")
    print(f"Daily Return:       {np.exp(current_log_ret)-1:.2%}")
    print(f"Current Drawdown:   {df['Drawdown'].iloc[-1]*100:.2f}%")
    print(f"VIX Index:          {df['VIX'].iloc[-1]:.2f}")
    print(f"Yield Curve Slope:  {df['Slope'].iloc[-1]:.2f}%")
    print("-" * 60)
    print(f"Lifetime Sigma (σ): {lifetime_sigma:.6f}")
    print(f"Lifetime MAD:       {lifetime_mad:.6f}")
    print("-" * 60)
    print(f"Move Severity (σ):  {current_sigma_move:+.2f} σ")
    print(f"Move Severity (MAD):{current_mad_move:+.2f} MAD")
    print("="*60)

    # 5. Visualization
    dashboard = MatplotlibDashboard()
    context = {
        'lifetime_sigma': lifetime_sigma,
        'lifetime_mad': lifetime_mad
    }
    dashboard.render(df, context)

if __name__ == "__main__":
    main()

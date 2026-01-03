import sys
import logging
import pandas as pd
import argparse
from datetime import datetime
from market_monitor.data.adapters import YahooFinanceAdapter, FredAdapter
from market_monitor.data.store import ParquetStore
from market_monitor.data.manager import fetch_and_update
from market_monitor.analytics.math_lib import get_log_returns, calculate_drawdown
from market_monitor.ui.dashboard import MatplotlibDashboard
from market_monitor.ui.reporter import print_report

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
TICKER_SPX = "^GSPC"
TICKER_VIX = "^VIX"
TICKER_SLOPE = "T10Y3M" # FRED Series ID
TICKER_RECESSION = "USREC" # FRED Recession Indicator
DEFAULT_START_DATE = "1927-12-30"

def main():
    parser = argparse.ArgumentParser(description="Market Monitor")
    parser.add_argument("--offline", action="store_true", help="Use local data only, do not fetch new data")
    parser.add_argument("--csv-path", type=str, help="Path to CSV file (Legacy/Override)")
    args = parser.parse_args()

    logger.info(f"--- [MARKET MONITOR] {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---")

    store = ParquetStore()

    # Adapters
    adapter_yahoo = YahooFinanceAdapter(use_cache=False)
    adapter_fred = FredAdapter(use_cache=False)

    # 1. Ingestion & Delta Update
    if args.offline:
        logger.info("[*] Mode: OFFLINE")
        df_spx = store.load(TICKER_SPX)
        df_vix = store.load(TICKER_VIX)
        df_slope = store.load(TICKER_SLOPE)
        df_recession = store.load(TICKER_RECESSION)
    else:
        logger.info("[*] Mode: ONLINE (Delta Sync)")
        df_spx = fetch_and_update(TICKER_SPX, adapter_yahoo, store, DEFAULT_START_DATE)
        df_vix = fetch_and_update(TICKER_VIX, adapter_yahoo, store, "1990-01-01") # VIX usually starts 1990
        df_slope = fetch_and_update(TICKER_SLOPE, adapter_fred, store, DEFAULT_START_DATE)
        df_recession = fetch_and_update(TICKER_RECESSION, adapter_fred, store, "1850-01-01") # Fetch full history

    if df_spx is None or df_spx.empty:
        logger.error("[!] Error: No SPX data available.")
        sys.exit(1)

    # 2. Normalization & Alignment
    # We need a master dataframe aligned to SPX trading days
    df = pd.DataFrame(index=df_spx.index)

    # Extract Series.
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
        elif 'USREC' in df_in.columns:
            return df_in['USREC']
        else:
            return df_in.iloc[:, 0]

    df['SPX'] = extract_series(df_spx, TICKER_SPX)

    # Join VIX and Slope (forward fill for days when macro data is missing but market is open?)
    # Usually we want to align to SPX index.
    s_vix = extract_series(df_vix, TICKER_VIX)
    s_slope = extract_series(df_slope, TICKER_SLOPE)
    s_rec = extract_series(df_recession, TICKER_RECESSION)

    # Reindex to match SPX
    df['VIX'] = s_vix.reindex(df.index, method='ffill')
    df['Slope'] = s_slope.reindex(df.index, method='ffill')
    df['Recession'] = s_rec.reindex(df.index, method='ffill')

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
    print_report(df, current_sigma_move, current_mad_move, lifetime_sigma, lifetime_mad)

    # 5. Visualization
    dashboard = MatplotlibDashboard()
    context = {
        'lifetime_sigma': lifetime_sigma,
        'lifetime_mad': lifetime_mad
    }
    dashboard.render(df, context)

if __name__ == "__main__":
    main()

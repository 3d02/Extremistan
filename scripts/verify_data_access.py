import pandas as pd
from extremistan.data.adapters import YahooFinanceAdapter, FredAdapter

def verify_adapters():
    print("Verifying Adapters...")

    # Yahoo Verification
    yf_adapter = YahooFinanceAdapter(use_cache=False)
    tickers = ['^VIX', '^VIX3M', '^SKEW', '^GSPC']
    print(f"Fetching Yahoo Tickers: {tickers}")
    df_yf = yf_adapter.get_data(tickers, start_date='2020-01-01')

    if df_yf.empty:
        print("ERROR: Yahoo Data is empty.")
    else:
        print("Yahoo Data Head:")
        print(df_yf.head())
        print("Yahoo Data Columns:", df_yf.columns)

    # FRED Verification
    fred_adapter = FredAdapter(use_cache=False)
    fred_ticker = ['T10Y3M']
    print(f"Fetching FRED Ticker: {fred_ticker}")
    df_fred = fred_adapter.get_data(fred_ticker, start_date='2020-01-01')

    if df_fred.empty:
        print("ERROR: FRED Data is empty.")
    else:
        print("FRED Data Head:")
        print(df_fred.head())

    # Check alignment capability
    print("\nAligning Indices (Intersection)...")
    if not df_yf.empty and not df_fred.empty:
        # Ensure timezone-naive for FRED too (adapter might not do it by default yet, let's check)
        if df_fred.index.tz is not None:
             df_fred.index = df_fred.index.tz_localize(None)

        aligned = pd.concat([df_yf, df_fred], axis=1, join='inner')
        print(f"Aligned Data Rows: {len(aligned)}")
        print(aligned.head())

if __name__ == "__main__":
    verify_adapters()

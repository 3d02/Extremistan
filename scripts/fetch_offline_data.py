import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import datetime
import os
from typing import List

# Configuration
YAHOO_TICKERS = ["^GSPC", "^VIX", "^MOVE"]
FRED_TICKERS = ["T10Y3M", "USREC"]
START_DATE = "1927-12-30"
OUTPUT_PATH = "data_storage/sp500_history_1927_2025.csv"

def fetch_data():
    print("--- [OFFLINE DATA FETCH] ---")

    # 1. Fetch Yahoo Data
    print(f"[*] Fetching Yahoo Data: {YAHOO_TICKERS}")
    try:
        df_yahoo = yf.download(YAHOO_TICKERS, start=START_DATE, progress=True, auto_adjust=True)
        # Flatten MultiIndex if necessary
        if isinstance(df_yahoo.columns, pd.MultiIndex):
            if 'Close' in df_yahoo.columns:
                 df_yahoo = df_yahoo['Close']
    except Exception as e:
        print(f"[!] Yahoo Fetch Error: {e}")
        df_yahoo = pd.DataFrame()

    # 2. Fetch FRED Data
    print(f"[*] Fetching FRED Data: {FRED_TICKERS}")
    try:
        # Use a recent end date (today)
        end_date = datetime.datetime.now()
        df_fred = web.DataReader(FRED_TICKERS, 'fred', START_DATE, end_date)
    except Exception as e:
        print(f"[!] FRED Fetch Error: {e}")
        df_fred = pd.DataFrame()

    # 3. Merge
    print("[*] Merging Datasets...")
    if df_yahoo.empty and df_fred.empty:
        print("[!] No data fetched.")
        return

    if df_yahoo.empty:
        df_final = df_fred
    elif df_fred.empty:
        df_final = df_yahoo
    else:
        # Ensure timezones are consistent (Yahoo is often tz-aware, FRED is naive)
        # We normalize to naive for storage
        if df_yahoo.index.tz is not None:
            df_yahoo.index = df_yahoo.index.tz_localize(None)
        if df_fred.index.tz is not None:
            df_fred.index = df_fred.index.tz_localize(None)

        df_final = df_yahoo.join(df_fred, how='outer')

    # 4. Save
    # Ensure directory exists
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

    print(f"[*] Saving to {OUTPUT_PATH}...")
    df_final.to_csv(OUTPUT_PATH)
    print("[*] Done.")

if __name__ == "__main__":
    fetch_data()

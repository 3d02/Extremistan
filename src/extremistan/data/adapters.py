import pandas as pd
import yfinance as yf
import numpy as np
from typing import List, Optional
from extremistan.data.interfaces import DataSource
from extremistan.data.store import ParquetStore

class YahooFinanceAdapter(DataSource):
    """
    Fetches data from Yahoo Finance API.
    Includes caching via ParquetStore.
    """
    def __init__(self, use_cache: bool = True):
        self.store = ParquetStore() if use_cache else None

    def get_data(self, tickers: List[str], start_date: str, end_date: Optional[str] = None) -> pd.DataFrame:
        # 1. Try Cache
        if self.store:
            cached_data = self.store.load(tickers, start_date, end_date)
            if cached_data is not None:
                return cached_data

        # 2. Fetch Live
        # yfinance download
        data = yf.download(tickers, start=start_date, end=end_date, auto_adjust=True, progress=False)

        if data.empty:
            return pd.DataFrame()

        # 3. Standardize Structure
        # We expect specific columns SPX and VIX usually.
        # But this adapter should be generic enough to return the raw data frame
        # or a standardized one.
        # For this specific project, the consuming code expects columns 'SPX' and 'VIX'.
        # However, the Adapter should probably return the multi-index or flattened frame
        # and let the caller map it, OR map it here if we know the mapping.

        # Let's standardize here to match the target architecture requirements:
        # "Pandas as Common Tongue: All modules exchange data via Pandas DataFrames/Series."

        # For simplicity in this project context, we will try to extract 'Close' prices.
        try:
             # Handle MultiIndex vs Single Index
            if isinstance(data.columns, pd.MultiIndex):
                # data['Close'] contains columns for each ticker
                df_close = data['Close'].copy()
            else:
                # Single ticker, data columns are 'Open', 'High', 'Low', 'Close', ...
                # We rename 'Close' to the ticker name for consistency if we can
                # But yf.download usually returns multiindex if list passed, even of length 1?
                # Actually yf.download(..., group_by='column') is default.
                if 'Close' in data.columns:
                     df_close = pd.DataFrame(data['Close'])
                     # If only one ticker requested, we might not know its name here easily
                     # without looking at input `tickers`.
                     if len(tickers) == 1:
                         df_close.columns = tickers
                else:
                    df_close = data # Fallback

            # Ensure index is DatetimeIndex
            df_close.index = pd.to_datetime(df_close.index)

            # 4. Save to Cache
            if self.store:
                self.store.save(df_close, tickers, start_date, end_date)

            return df_close

        except Exception as e:
            print(f"Error processing Yahoo data: {e}")
            return pd.DataFrame()

class CSVAdapter(DataSource):
    """
    Loads data from a local CSV file.
    Assumes CSV has a Date index and columns matching tickers.
    """
    def __init__(self, filepath: str):
        self.filepath = filepath

    def get_data(self, tickers: List[str], start_date: str, end_date: Optional[str] = None) -> pd.DataFrame:
        try:
            df = pd.read_csv(self.filepath, index_col=0, parse_dates=True)

            # Filter by date
            if start_date:
                df = df[df.index >= pd.to_datetime(start_date)]
            if end_date:
                df = df[df.index <= pd.to_datetime(end_date)]

            # Filter columns if they exist
            available_cols = [t for t in tickers if t in df.columns]
            if available_cols:
                return df[available_cols]
            else:
                # Fallback: if columns don't match ticker names (e.g. CSV has 'SPX' but we asked for '^GSPC')
                # We might return the whole thing or try to map.
                # For this specific task, we know the CSV structure likely matches what we need or we return all.
                return df
        except FileNotFoundError:
            print(f"File not found: {self.filepath}")
            return pd.DataFrame()

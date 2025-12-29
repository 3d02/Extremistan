import pandas as pd
import yfinance as yf
import pandas_datareader.data as web
import numpy as np
from typing import List, Optional
from extremistan.data.interfaces import DataSource
from extremistan.data.store import ParquetStore

class FredAdapter(DataSource):
    """
    Fetches economic data from FRED (Federal Reserve Economic Data).
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
        try:
            # pandas_datareader syntax for FRED: web.DataReader(tickers, 'fred', start, end)
            data = web.DataReader(tickers, 'fred', start_date, end_date)

            if data.empty:
                return pd.DataFrame()

            # Ensure index is DatetimeIndex
            data.index = pd.to_datetime(data.index)

            # 3. Save to Cache
            if self.store:
                self.store.save(data, tickers, start_date, end_date)

            return data

        except Exception as e:
            print(f"Error processing FRED data: {e}")
            return pd.DataFrame()

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
        # "Pandas as Common Tongue: All modules exchange data via Pandas DataFrames/Series."

        # We handle multi-index outputs from yfinance
        try:
            df_close = pd.DataFrame()

            # Check if we have a MultiIndex columns (happens when downloading multiple tickers)
            if isinstance(data.columns, pd.MultiIndex):
                # If 'Close' is at the top level
                if 'Close' in data.columns.levels[0]:
                    df_close = data['Close'].copy()
                # If 'Close' is at the second level (some versions of yf)
                elif 'Close' in data.columns.get_level_values(1):
                    # We need to extract the 'Close' slice
                     df_close = data.xs('Close', level=1, axis=1).copy()
                else:
                     # Fallback to just using the data as is, assuming user knows structure
                     # Or try to find 'Close'
                     if 'Close' in data.columns:
                         df_close = data['Close'].copy()
                     else:
                         df_close = data.copy() # Last resort

            else:
                # Single level index
                if 'Close' in data.columns:
                    df_close = pd.DataFrame(data['Close'])
                    # If only one ticker requested, rename column to ticker
                    if len(tickers) == 1:
                        df_close.columns = tickers
                else:
                    df_close = data.copy()

            # Ensure index is DatetimeIndex and timezone-naive to prevent merge issues
            df_close.index = pd.to_datetime(df_close.index)
            if df_close.index.tz is not None:
                df_close.index = df_close.index.tz_localize(None)

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

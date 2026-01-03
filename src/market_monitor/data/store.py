import os
import pandas as pd
from typing import Optional
from datetime import datetime

class ParquetStore:
    """
    Local caching mechanism using Parquet files with per-ticker delta updates.
    """
    def __init__(self, cache_dir: str = "data_storage"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _get_filepath(self, ticker: str) -> str:
        """Generates a filename based on the ticker symbol."""
        # Sanitize ticker for filename (e.g., ^GSPC -> GSPC)
        safe_ticker = ticker.replace("^", "").replace("=", "_")
        return os.path.join(self.cache_dir, f"{safe_ticker}.parquet")

    def load(self, ticker: str) -> Optional[pd.DataFrame]:
        """Loads data for a specific ticker from cache if it exists."""
        filepath = self._get_filepath(ticker)
        if os.path.exists(filepath):
            try:
                df = pd.read_parquet(filepath)
                # Ensure index is datetime and sorted
                if not isinstance(df.index, pd.DatetimeIndex):
                    df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                return df
            except Exception as e:
                print(f"[!] Cache read error for {ticker}: {e}")
                return None
        return None

    def get_last_date(self, ticker: str) -> Optional[datetime]:
        """Returns the last available date in the cache for the given ticker."""
        df = self.load(ticker)
        if df is not None and not df.empty:
            return df.index[-1]
        return None

    def save(self, data: pd.DataFrame, ticker: str):
        """Saves or updates data for a specific ticker."""
        if data is None or data.empty:
            return

        filepath = self._get_filepath(ticker)

        # Load existing data to merge if possible, or just overwrite/create if we are doing a full fetch context
        # But `save` is usually called after we have the *full* desired dataframe or the *delta*.
        # Our strategy is: load existing, fetch delta, merge in memory, then save full.
        # So this method assumes `data` is the COMPLETED dataset to be stored.

        try:
            # Ensure consistency
            data = data.sort_index()
            # Remove duplicates just in case
            data = data[~data.index.duplicated(keep='last')]
            data.to_parquet(filepath)
        except Exception as e:
            print(f"[!] Cache write error for {ticker}: {e}")

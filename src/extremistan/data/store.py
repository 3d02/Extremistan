import os
import hashlib
import pandas as pd
from typing import Optional, List
from datetime import datetime

class ParquetStore:
    """
    Local caching mechanism using Parquet files.
    """
    def __init__(self, cache_dir: str = ".cache"):
        self.cache_dir = cache_dir
        if not os.path.exists(cache_dir):
            os.makedirs(cache_dir)

    def _generate_key(self, tickers: List[str], start_date: str, end_date: Optional[str]) -> str:
        """Generates a unique filename based on the request parameters."""
        # Sort tickers to ensure same key for same set
        sorted_tickers = sorted(tickers)
        raw_key = f"{'_'.join(sorted_tickers)}_{start_date}_{end_date}"
        hash_key = hashlib.md5(raw_key.encode()).hexdigest()
        return os.path.join(self.cache_dir, f"{hash_key}.parquet")

    def load(self, tickers: List[str], start_date: str, end_date: Optional[str] = None) -> Optional[pd.DataFrame]:
        """Loads data from cache if it exists."""
        filepath = self._generate_key(tickers, start_date, end_date)
        if os.path.exists(filepath):
            try:
                # print(f"DEBUG: Loading from cache: {filepath}")
                return pd.read_parquet(filepath)
            except Exception as e:
                # print(f"DEBUG: Cache read error: {e}")
                return None
        return None

    def save(self, data: pd.DataFrame, tickers: List[str], start_date: str, end_date: Optional[str] = None):
        """Saves data to cache."""
        if data is None or data.empty:
            return
        filepath = self._generate_key(tickers, start_date, end_date)
        try:
            data.to_parquet(filepath)
        except Exception as e:
            # print(f"DEBUG: Cache write error: {e}")
            pass

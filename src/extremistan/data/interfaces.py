from typing import Protocol, List, Optional
import pandas as pd
from abc import abstractmethod

class DataSource(Protocol):
    """Interface for data ingestion adapters."""

    @abstractmethod
    def get_data(self, tickers: List[str], start_date: str, end_date: Optional[str] = None) -> pd.DataFrame:
        """
        Fetch historical data for the given tickers.

        Returns:
            pd.DataFrame: DataFrame containing Price (Close) and VIX data.
                          Columns should be MultiIndex (Ticker, Attribute) or Flat if standardized.
                          Standardized output preferred: Index=Date, Columns=['SPX', 'VIX']
        """
        ...

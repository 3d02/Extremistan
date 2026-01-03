import logging
import pandas as pd
from datetime import datetime, timedelta
from typing import Optional, List
from market_monitor.data.store import ParquetStore

# Configure logging
logger = logging.getLogger(__name__)

def fetch_and_update(
    ticker: str,
    adapter,
    store: ParquetStore,
    start_date_default: str
) -> pd.DataFrame:
    """
    Fetches data for a ticker using delta logic:
    1. Load existing data.
    2. Determine start date (Last Date + 1 or Default).
    3. Fetch new data.
    4. Merge and Save.
    5. Return full dataframe.

    Args:
        ticker: The ticker symbol to fetch.
        adapter: The data adapter instance (YahooFinanceAdapter or FredAdapter).
        store: The ParquetStore instance.
        start_date_default: The default start date if no data exists.

    Returns:
        pd.DataFrame: The complete dataframe for the ticker.
    """
    logger.info(f"Processing {ticker}...")

    # 1. Load Existing
    df_existing: Optional[pd.DataFrame] = store.load(ticker)

    start_date = start_date_default
    if df_existing is not None and not df_existing.empty:
        last_date = df_existing.index[-1]
        # Start from next day
        start_date = (last_date + timedelta(days=1)).strftime('%Y-%m-%d')
        logger.debug(f"Found existing data up to {last_date.strftime('%Y-%m-%d')}. Fetching delta from {start_date}...")
    else:
        logger.debug(f"No existing data. Fetching full history from {start_date}...")
        df_existing = pd.DataFrame()

    # 2. Fetch New (if needed)
    # Check if start_date is in the future
    if pd.to_datetime(start_date) > datetime.now():
        logger.debug("Data is up to date.")
        return df_existing if df_existing is not None else pd.DataFrame()

    try:
        # Adapter expects list of tickers
        # Note: We assume the adapter follows the Protocol with get_data(tickers, start_date)
        df_new = adapter.get_data([ticker], start_date=start_date)
    except Exception as e:
        logger.error(f"Error fetching {ticker}: {e}")
        df_new = pd.DataFrame()

    # 3. Merge
    if df_new.empty:
        return df_existing if df_existing is not None else pd.DataFrame()

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

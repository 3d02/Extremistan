import pandas as pd
import pytest
from unittest.mock import MagicMock, patch
from market_monitor.data.adapters import YahooFinanceAdapter, CSVAdapter
from market_monitor.data.store import ParquetStore
import os
import shutil

# --- Test ParquetStore ---
@pytest.fixture
def clean_cache():
    cache_dir = ".test_cache"
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    yield cache_dir
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)

def test_store_save_load(clean_cache):
    store = ParquetStore(cache_dir=clean_cache)
    df = pd.DataFrame({'A': [1, 2, 3]}, index=pd.to_datetime(['2020-01-01', '2020-01-02', '2020-01-03']))

    ticker = 'TEST'

    # Save
    store.save(df, ticker)

    # Load
    loaded_df = store.load(ticker)

    assert loaded_df is not None
    pd.testing.assert_frame_equal(df, loaded_df)

def test_store_miss(clean_cache):
    store = ParquetStore(cache_dir=clean_cache)
    loaded_df = store.load('MISSING')
    assert loaded_df is None

# --- Test Adapters ---

def test_csv_adapter(tmp_path):
    # Create a dummy CSV
    d = tmp_path / "data.csv"
    df = pd.DataFrame({'SPX': [100, 101], 'VIX': [20, 19]}, index=pd.to_datetime(['2023-01-01', '2023-01-02']))
    df.to_csv(d)

    adapter = CSVAdapter(filepath=str(d))
    result = adapter.get_data(['SPX'], start_date='2023-01-01')

    assert not result.empty
    assert 'SPX' in result.columns
    assert len(result) == 2

@patch('yfinance.download')
def test_yahoo_adapter_no_cache(mock_download):
    # Mock return data
    # Standard Yahoo Finance structure (MultiIndex columns)
    arrays = [['Close', 'Close'], ['SPX', 'VIX']]
    tuples = list(zip(*arrays))
    index = pd.MultiIndex.from_tuples(tuples, names=['Price', 'Ticker'])

    mock_data = pd.DataFrame(
        [[100, 20], [101, 19]],
        index=pd.to_datetime(['2023-01-01', '2023-01-02']),
        columns=index
    )

    mock_download.return_value = mock_data

    adapter = YahooFinanceAdapter(use_cache=False)
    result = adapter.get_data(['SPX', 'VIX'], '2023-01-01')

    assert not result.empty
    assert 'SPX' in result.columns
    assert 'VIX' in result.columns
    mock_download.assert_called_once()

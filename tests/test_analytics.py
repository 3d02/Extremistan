import numpy as np
import pandas as pd
import pytest
from market_monitor.analytics.math_lib import get_log_returns, calculate_drawdown

def test_get_log_returns():
    prices = pd.Series([100, 105, 102, 110])
    returns = get_log_returns(prices)

    assert np.isnan(returns.iloc[0]) # First element is always NaN
    assert np.isclose(returns.iloc[1], np.log(105/100))
    assert np.isclose(returns.iloc[2], np.log(102/105))

def test_calculate_drawdown():
    prices = pd.Series([100, 120, 108, 130, 117])
    dd = calculate_drawdown(prices)

    # 100 -> HWM 100 -> DD 0
    assert dd.iloc[0] == 0.0
    # 120 -> HWM 120 -> DD 0
    assert dd.iloc[1] == 0.0
    # 108 -> HWM 120 -> DD (108/120 - 1) = -0.1
    assert np.isclose(dd.iloc[2], -0.1)
    # 130 -> HWM 130 -> DD 0
    assert dd.iloc[3] == 0.0
    # 117 -> HWM 130 -> DD (117/130 - 1) = -0.1
    assert np.isclose(dd.iloc[4], -0.1)

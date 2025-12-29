import numpy as np
import pandas as pd
import pytest
from src.extremistan.analytics.math_lib import get_log_returns, get_hill_alpha, calculate_drawdown

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

def test_hill_alpha_basic():
    # Construct a Pareto-like tail
    # If X follows Pareto(alpha), P(X > x) = (xm/x)^alpha
    # We want to check if the estimator converges roughly for a synthetic dataset
    np.random.seed(42)
    alpha_true = 3.0
    xm = 1.0

    # Inverse transform sampling: U ~ Uniform(0,1), X = xm * (1-U)^(-1/alpha)
    n_samples = 2000
    u = np.random.uniform(0, 1, n_samples)
    losses = xm * (1 - u)**(-1.0/alpha_true)

    # Create a series where "losses" are positive values, but the function expects
    # a series of returns where losses are negative.
    # So we negate them.
    returns = pd.Series(-losses)

    alpha_est = get_hill_alpha(returns, k_pct=0.1) # Use top 10%

    # It's an estimator, so allow some error margin (e.g., +/- 0.5)
    assert 2.5 < alpha_est < 3.5

def test_hill_alpha_insufficient_data():
    series = pd.Series(np.random.randn(10)) # Too few
    assert np.isnan(get_hill_alpha(series))

def test_hill_alpha_no_losses():
    series = pd.Series([0.01, 0.02, 0.03]) # All positive
    assert np.isnan(get_hill_alpha(series))

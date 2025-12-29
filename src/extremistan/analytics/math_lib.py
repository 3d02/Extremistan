import numpy as np
import pandas as pd

def get_log_returns(series: pd.Series) -> pd.Series:
    """
    Calculates logarithmic returns from a price series.
    Formula: r_t = ln(P_t / P_{t-1})
    """
    return np.log(series / series.shift(1))

def get_hill_alpha(series: pd.Series, k_pct: float = 0.05, min_k: int = 10) -> float:
    """
    Calculates the Hill Estimator for Tail Index Alpha.

    Args:
        series: Pandas Series of returns (usually log returns).
        k_pct: The percentage of tail observations to consider (default 0.05).
        min_k: The minimum number of tail observations required to calculate Alpha (default 10).

    Returns:
        float: The Hill Index (Alpha). Returns np.nan if insufficient data.
    """
    # Filter for losses (negative returns) and convert to positive magnitude
    losses = -series[series < 0]
    losses = losses.dropna()

    n = len(losses)
    if n == 0:
        return np.nan

    k = int(n * k_pct)
    if k < min_k:
        return np.nan

    # Sort losses descending (largest loss first)
    sorted_losses = np.sort(losses.values)[::-1]

    top_k = sorted_losses[:k]
    threshold = sorted_losses[k] # X_(k+1) in some formulations, or X_k. Using k-th (0-indexed) as threshold implies we take top k greater than threshold.

    # Avoid division by zero or log of zero/negative (shouldn't happen with filtered losses > 0)
    if threshold <= 0:
        return np.nan

    # Hill Estimator Formula:
    # Xi = (1/k) * Sum( log(X_i / X_threshold) ) for i=1 to k
    # Alpha = 1 / Xi
    xi = np.mean(np.log(top_k / threshold))

    return 1.0 / xi if xi > 0 else np.nan

def calculate_drawdown(series: pd.Series) -> pd.Series:
    """
    Calculates the drawdown series from a price series.
    Drawdown = (Price / High_Water_Mark) - 1
    """
    high_water_mark = series.expanding().max()
    return (series / high_water_mark) - 1

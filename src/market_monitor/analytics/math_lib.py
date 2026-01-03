import numpy as np
import pandas as pd

def get_log_returns(series: pd.Series) -> pd.Series:
    """
    Calculates logarithmic returns from a price series.
    Formula: r_t = ln(P_t / P_{t-1})
    """
    return np.log(series / series.shift(1))

def calculate_drawdown(series: pd.Series) -> pd.Series:
    """
    Calculates the drawdown series from a price series.
    Drawdown = (Price / High_Water_Mark) - 1
    """
    high_water_mark = series.expanding().max()
    return (series / high_water_mark) - 1

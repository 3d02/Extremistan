import pytest
import pandas as pd
import numpy as np
from extremistan.analytics.math_lib import get_hill_alpha, get_rolling_volatility, get_z_score
from extremistan.strategy.signal_engine import SignalEngine

def test_adaptive_hill_alpha_logic():
    # Generate synthetic data with fat tails
    np.random.seed(42)
    # Pareto distribution
    data = (np.random.pareto(a=3.0, size=1000) + 1) * 2
    # Convert to "returns" centered around 0, some negative
    returns = pd.Series(np.random.normal(0, 0.01, 1000))
    # Inject some large losses
    returns.iloc[:50] = -data[:50] * 0.01

    # Fixed k (old way)
    alpha_fixed = get_hill_alpha(returns, k_pct=0.05, adaptive=False)
    assert not np.isnan(alpha_fixed)

    # Adaptive k
    alpha_adaptive = get_hill_alpha(returns, adaptive=True, min_k=10)
    assert not np.isnan(alpha_adaptive)

    # Verify adaptive usually picks different k than fixed 5% if sqrt(n) != 0.05*n
    # n losses approx 500 (half negative). sqrt(500) ~ 22. 5% of 500 = 25.
    # Close but let's check exact behavior on small sample
    small_losses = pd.Series([-0.01] * 20 + [-0.05] * 5 + [-0.10]) # 26 losses
    # n=26. sqrt(26)=5. min_k=4. k_adaptive=5.
    # Fixed 5% of 26 = 1.3 -> 1.
    alpha_adapt_small = get_hill_alpha(small_losses, adaptive=True, min_k=4)
    alpha_fixed_small = get_hill_alpha(small_losses, k_pct=0.05, min_k=1, adaptive=False)

    # Different k implies potentially different alpha
    assert alpha_adapt_small != alpha_fixed_small

def test_signal_engine_cross_asset():
    engine = SignalEngine()

    # Case 1: Extremistan + Fragile + No Stress -> GO
    res = engine.evaluate(
        alpha_2y=2.5,
        alpha_6m=2.0,
        fragility_density=0.8,
        healing_density=0.1,
        slope=1.0,
        move_index=100
    )
    assert res.signal == "GO"
    assert "High Conviction" not in res.description # Standard GO

    # Case 2: Extremistan + Fragile + Stress (Inverted Slope) -> GO (High Conviction)
    res = engine.evaluate(
        alpha_2y=2.5,
        alpha_6m=2.0,
        fragility_density=0.8,
        healing_density=0.1,
        slope=-0.5,
        move_index=100
    )
    assert res.signal == "GO"
    assert "HIGH CONVICTION" in res.description

    # Case 3: Extremistan + Fragile + Stress (High MOVE) -> GO (High Conviction)
    res = engine.evaluate(
        alpha_2y=2.5,
        alpha_6m=2.0,
        fragility_density=0.8,
        healing_density=0.1,
        slope=1.0,
        move_index=130
    )
    assert res.signal == "GO"
    assert "HIGH CONVICTION" in res.description

def test_signal_engine_healing():
    engine = SignalEngine()

    # Case: Extremistan + Fragile Density High BUT Healing Density ALSO High -> WATCH
    res = engine.evaluate(
        alpha_2y=2.5,
        alpha_6m=3.0, # Weather > Climate locally
        fragility_density=0.6, # Still high from history
        healing_density=0.6, # But healing is dominating recently?
        slope=1.0,
        move_index=100
    )
    assert res.signal == "WATCH"
    assert "Healing Detected" in res.description

def test_rolling_regime_metrics():
    s = pd.Series(np.random.normal(0, 1, 100))
    vol = get_rolling_volatility(s, window=10)
    assert len(vol) == 100
    assert np.isnan(vol.iloc[8]) # First 9 are NaN
    assert not np.isnan(vol.iloc[9])

    z = get_z_score(2.0, 0.0, 1.0)
    assert z == 2.0

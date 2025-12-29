import pytest
from extremistan.strategy.signal_engine import SignalEngine

def test_signal_go():
    engine = SignalEngine()
    # 2Y is very low (risk), High Fragility Density (>0.5)
    # Standard GO (Fragility only), no Cross-Asset Stress
    res = engine.evaluate(alpha_2y=2.5, alpha_26w=2.0, fragility_density=0.6)
    assert res.signal == "GO"
    assert "Fragile Regime" in res.description
    assert "Density 60%" in res.description

def test_signal_watch_low_density():
    engine = SignalEngine()
    # 2Y is low (risk), but Density is low (<=0.5)
    res = engine.evaluate(alpha_2y=2.5, alpha_26w=2.0, fragility_density=0.4)
    assert res.signal == "WATCH"
    assert "Wait for Density" in res.description

def test_signal_caution():
    engine = SignalEngine()
    # 2Y is between 3.0 and 3.5, Density irrelevant but low
    res = engine.evaluate(alpha_2y=3.2, alpha_26w=3.0, fragility_density=0.4)
    assert res.signal == "CAUTION"

def test_signal_nogo():
    engine = SignalEngine()
    # 2Y is healthy (> 3.5)
    res = engine.evaluate(alpha_2y=4.0, alpha_26w=3.0)
    assert res.signal == "NO-GO"

def test_signal_nan():
    engine = SignalEngine()
    res = engine.evaluate(alpha_2y=float('nan'), alpha_26w=3.0)
    assert res.signal == "NO-GO"

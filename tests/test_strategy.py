import pytest
from src.extremistan.strategy.signal_engine import SignalEngine

def test_signal_go():
    engine = SignalEngine()
    # 2Y is very low (risk), 6M is even lower (deteriorating)
    res = engine.evaluate(alpha_2y=2.5, alpha_6m=2.0)
    assert res.signal == "GO"
    assert "High Conviction" in res.description

def test_signal_watch():
    engine = SignalEngine()
    # 2Y is low (risk), but 6M is higher (healing/better than long term)
    res = engine.evaluate(alpha_2y=2.5, alpha_6m=2.8)
    assert res.signal == "WATCH"

def test_signal_caution():
    engine = SignalEngine()
    # 2Y is between 3.0 and 3.5
    res = engine.evaluate(alpha_2y=3.2, alpha_6m=3.0)
    assert res.signal == "CAUTION"

def test_signal_nogo():
    engine = SignalEngine()
    # 2Y is healthy (> 3.5)
    res = engine.evaluate(alpha_2y=4.0, alpha_6m=3.0)
    assert res.signal == "NO-GO"

def test_signal_nan():
    engine = SignalEngine()
    res = engine.evaluate(alpha_2y=float('nan'), alpha_6m=3.0)
    assert res.signal == "NO-GO"

import pandas as pd
import numpy as np
from extremistan.strategy.probabilistic_engine import ProbabilisticEngine

def verify_engine():
    print("Verifying Probabilistic Engine...")

    # 1. Create Dummy History
    dates = pd.date_range(start='2020-01-01', periods=500, freq='B')
    data = {
        'Alpha_2Y': np.random.normal(3.0, 0.5, 500),
        'Alpha_6M': np.random.normal(3.0, 0.5, 500),
        'Slope': np.random.normal(0.5, 0.2, 500),
        'VIX': np.random.normal(20, 5, 500),
        'VIX_Curve': np.random.normal(1.0, 0.1, 500),
        'SKEW': np.random.normal(120, 10, 500),
        'SPX': np.linspace(3000, 4000, 500) # Bull market
    }
    # Add a crash scenario
    data['SPX'][400:420] = data['SPX'][400:420] * 0.8

    df_hist = pd.DataFrame(data, index=dates)

    engine = ProbabilisticEngine(df_hist)

    # 2. Test Matching
    # Pick a day from history as "current"
    current_vec = df_hist.iloc[100]

    print("\nFinding matching regimes...")
    matches = engine.find_similar_regimes(current_vec, n_neighbors=10)
    print(f"Found {len(matches)} matches.")
    print(matches)

    # 3. Test Probabilities
    print("\nCalculating Probabilities...")
    probs = engine.calculate_probabilities(matches, maturities_months=[1, 3], otm_strikes_pct=[0.05, 0.20])
    print(probs)

    # Expected output: DataFrame 2x2
    if probs.shape == (2, 2):
        print("SUCCESS: Probability matrix shape is correct.")
    else:
        print(f"ERROR: Unexpected shape {probs.shape}")

if __name__ == "__main__":
    verify_engine()

import sys
import pandas as pd
import numpy as np
import argparse
from datetime import datetime
from extremistan.analytics.regime import RegimeAnalytics
from extremistan.strategy.probabilistic_engine import ProbabilisticEngine
from extremistan.ui.dashboard import MatplotlibDashboard

# Configuration
TICKER = "^GSPC"

def main():
    parser = argparse.ArgumentParser(description="Extremistan Tail Risk Monitor")
    parser.add_argument("--start-date", type=str, default="2007-01-01", help="Start date for regime analysis")
    parser.add_argument("--n-matches", type=int, default=50, help="Number of historical matches to find")
    args = parser.parse_args()

    print(f"--- [COMMAND CENTER] INITIALIZING FOR {TICKER} ---")

    # 1. Initialize Regime Analytics & Build Feature Matrix
    print("[*] Building Historical Feature Matrix...")
    regime_analytics = RegimeAnalytics()
    feature_matrix = regime_analytics.build_feature_matrix(start_date=args.start_date)

    if feature_matrix.empty:
        print("[!] Error: Feature matrix is empty. Cannot proceed.")
        sys.exit(1)

    # 2. Probabilistic Engine
    engine = ProbabilisticEngine(feature_matrix)

    # Get Current State (Last available row)
    current_state = feature_matrix.iloc[-1]
    current_date = feature_matrix.index[-1]

    print("\n" + "="*60)
    print(f"TAIL-RISK OPERATIONAL BRIEFING: {datetime.now().strftime('%Y-%m-%d')}")
    print(f"Market Data Date:   {current_date.strftime('%Y-%m-%d')}")
    print("="*60)
    print(f"S&P 500 Level:      ${current_state['SPX']:,.2f}")
    print(f"VIX Level:          {current_state['VIX']:.2f}")
    print("-" * 60)
    print("REGIME METRICS:")
    print(f"Alpha 2Y (Climate): {current_state['Alpha_2Y']:.2f}")
    print(f"Alpha 6M (Weather): {current_state['Alpha_6M']:.2f}")
    print(f"Slope (10Y-3M):     {current_state['Slope']:.2f}")
    print(f"VIX/VIX3M Curve:    {current_state['VIX_Curve']:.2f}")
    print(f"SKEW Index:         {current_state['SKEW']:.2f}")
    print("="*60)

    # 3. Find Similar Regimes
    print(f"[*] Analyzing {args.n_matches} most similar historical days...")
    matches = engine.find_similar_regimes(current_state, n_neighbors=args.n_matches)

    # 4. Calculate Probabilities
    print("[*] Calculating Put Option ITM Probabilities...")
    probs = engine.calculate_probabilities(
        matches,
        maturities_months=[3, 4, 5, 6],
        otm_strikes_pct=[0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]
    )

    # 5. Output Table
    print("\nPROBABILITY OF ITM (%) BY MATURITY AND OTM STRIKE:")
    print("-" * 60)
    if not probs.empty:
        # Format as percentage
        print((probs * 100).round(1).to_markdown())
    else:
        print("Insufficient data to calculate probabilities.")
    print("-" * 60)

    # 6. Visualization (Optional - reusing dashboard if needed, but context changed)
    # The new engine changes the data structure significantly.
    # For now, we skip the legacy dashboard render as it expects specific columns like 'Drawdown' etc calculated in main.
    # The user asked for "2d table in the markdown" which is provided above.

if __name__ == "__main__":
    main()

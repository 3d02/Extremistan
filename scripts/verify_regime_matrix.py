from extremistan.analytics.regime import RegimeAnalytics

def verify_regime():
    print("Initializing Regime Analytics...")
    analytics = RegimeAnalytics()

    print("Building Feature Matrix (Short history for test)...")
    # Using a recent date to make it faster, but enough to trigger alpha calc requires pre-fetch
    # The class subtracts 3 years, so passing 2023 will fetch from 2020.
    df = analytics.build_feature_matrix(start_date='2023-01-01')

    print("\nFeature Matrix Result:")
    print(df.info())
    print(df.head())
    print(df.tail())

    expected_cols = ['Alpha_2Y', 'Alpha_6M', 'Slope', 'VIX', 'VIX_Curve', 'SKEW', 'SPX']
    missing = [c for c in expected_cols if c not in df.columns]
    if missing:
        print(f"ERROR: Missing columns: {missing}")
    else:
        print("SUCCESS: All columns present.")

if __name__ == "__main__":
    verify_regime()

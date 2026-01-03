import numpy as np
import pandas as pd

def print_report(
    df: pd.DataFrame,
    current_sigma_move: float,
    current_mad_move: float,
    lifetime_sigma: float,
    lifetime_mad: float
) -> None:
    """
    Prints the Market Monitor report to the console.

    Args:
        df: The main dataframe containing 'SPX', 'VIX', 'Slope', 'Drawdown'.
        current_sigma_move: The current move magnitude in sigma.
        current_mad_move: The current move magnitude in MAD.
        lifetime_sigma: The lifetime standard deviation.
        lifetime_mad: The lifetime mean absolute deviation.
    """
    # Calculate daily return for display
    current_log_ret = df['Log_Return'].iloc[-1]

    print("\n" + "="*60)
    print(f"MARKET MONITOR REPORT: {df.index[-1].strftime('%Y-%m-%d')}")
    print("="*60)
    print(f"S&P 500 Level:      ${df['SPX'].iloc[-1]:,.2f}")
    print(f"Daily Return:       {np.exp(current_log_ret)-1:.2%}")
    print(f"Current Drawdown:   {df['Drawdown'].iloc[-1]*100:.2f}%")
    print(f"VIX Index:          {df['VIX'].iloc[-1]:.2f}")
    print(f"Yield Curve Slope:  {df['Slope'].iloc[-1]:.2f}%")
    print("-" * 60)
    print(f"Lifetime Sigma (σ): {lifetime_sigma:.6f}")
    print(f"Lifetime MAD:       {lifetime_mad:.6f}")
    print("-" * 60)
    print(f"Move Severity (σ):  {current_sigma_move:+.2f} σ")
    print(f"Move Severity (MAD):{current_mad_move:+.2f} MAD")
    print("="*60)

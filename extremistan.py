import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime

# ==========================================
# CONFIGURATION & PARAMETERS
# ==========================================
TICKER = "^GSPC"
VIX_TICKER = "^VIX"
START_DATE = "1927-12-30"
CLIMATE_WINDOW = 504  # 2 Years
WEATHER_WINDOW = 126   # 6 Months
K_PERCENT = 0.05       # Top 5% of losses for Hill Estimator

def get_hill_alpha(series, k_pct=K_PERCENT):
    """Calculates the Hill Estimator for Tail Index Alpha."""
    losses = -series[series < 0]
    n = len(losses)
    k = int(n * k_pct)
    if k < 10: return np.nan
    sorted_losses = np.sort(losses)[::-1]
    top_k = sorted_losses[:k]
    threshold = sorted_losses[k]
    xi = np.mean(np.log(top_k / threshold))
    return 1.0 / xi if xi > 0 else np.nan

def run_dashboard():
    print(f"--- [COMMAND CENTER] INITIALIZING FOR {TICKER} ---")
    
    # 1. Data Ingestion
    # Downloading both SPX and VIX
    data = yf.download([TICKER, VIX_TICKER], start=START_DATE, auto_adjust=True)
    
    if data.empty:
        print("[!] Error: No data retrieved.")
        return

    # Robust Column Handling for yfinance versions
    try:
        # If MultiIndex (Ticker as columns)
        spx_price = data['Close'][TICKER]
        vix_price = data['Close'][VIX_TICKER]
    except KeyError:
        # If Flat Index (Maybe only one ticker returned or different format)
        if isinstance(data.columns, pd.MultiIndex):
             # Try accessing by level 0 if names don't match exactly
             spx_price = data.xs(TICKER, axis=1, level=1)['Close']
             vix_price = data.xs(VIX_TICKER, axis=1, level=1)['Close']
        else:
             print("[!] Warning: Data structure ambiguous. Using 'Close' as SPX.")
             spx_price = data['Close']
             vix_price = pd.Series(np.nan, index=data.index)

    # 2. DataFrame Construction
    df = pd.DataFrame(index=data.index)
    df['SPX'] = spx_price
    df['VIX'] = vix_price
    
    # Calculate Log Returns (The Atomic Unit of the Strategy)
    df['Log_Return'] = np.log(df['SPX'] / df['SPX'].shift(1))
    df = df.dropna(subset=['Log_Return'])
    
    # 3. Lifetime Baseline (The Fixed Yardstick)
    lifetime_sigma = df['Log_Return'].std()
    lifetime_mu = df['Log_Return'].mean()
    
    # 4. Dual-Window Alpha Calculation
    # Using raw=False to ensure Series are passed to the function
    print("[*] Calculating Tail Alphas (This may take a moment)...")
    df['Alpha_2Y'] = df['Log_Return'].rolling(window=CLIMATE_WINDOW).apply(get_hill_alpha, raw=False)
    df['Alpha_6M'] = df['Log_Return'].rolling(window=WEATHER_WINDOW).apply(get_hill_alpha, raw=False)
    
    # 5. Current State Metrics
    curr_alpha_2y = df['Alpha_2Y'].iloc[-1]
    curr_alpha_6m = df['Alpha_6M'].iloc[-1]
    curr_vix = df['VIX'].iloc[-1]
    
    # Drawdown Calculation
    high_water_mark = df['SPX'].expanding().max()
    df['Drawdown'] = (df['SPX'] / high_water_mark) - 1
    curr_dd = df['Drawdown'].iloc[-1]
    
    # 6. Signal Logic
    signal = "NO-GO (Neutral/Safe)"
    if curr_alpha_2y < 3.0:
        if curr_alpha_6m < curr_alpha_2y:
            signal = "GO (High Conviction Extremistan)"
        else:
            signal = "WATCH (Structural Fragility - Wait for local crack)"
    elif curr_alpha_2y < 3.5:
        signal = "CAUTION (Warning Zone)"

    # ==========================================
    # VERBOSE LOGGING (STDOUT)
    # ==========================================
    print("\n" + "="*60)
    print(f"TAIL-RISK OPERATIONAL BRIEFING: {datetime.now().strftime('%Y-%m-%d')}")
    print("="*60)
    print(f"S&P 500 Level:      ${df['SPX'].iloc[-1]:,.2f}")
    print(f"Current Drawdown:   {curr_dd*100:.2f}%")
    print(f"VIX Index:          {curr_vix:.2f} " + ("(High Panic)" if curr_vix > 30 else "(Low Fear)"))
    print("-" * 60)
    print(f"Lifetime Sigma (σ): {lifetime_sigma:.6f}")
    print(f"Today's Shock:      {(df['Log_Return'].iloc[-1] / lifetime_sigma):.2f}σ")
    print("-" * 60)
    print(f"Climate Alpha (2Y): {curr_alpha_2y:.2f}  [{'Extremistan' if curr_alpha_2y < 3 else 'Mediocristan'}]")
    print(f"Weather Alpha (6M): {curr_alpha_6m:.2f}  [{'Fragilizing' if curr_alpha_6m < curr_alpha_2y else 'Healing'}]")
    print("-" * 60)
    print(f"STRATEGIC SIGNAL:   {signal}")
    print("="*60)

    # ==========================================
    # INTERACTIVE DASHBOARD (4 TRACKS)
    # ==========================================
    # Increased height to accommodate 4 distinct plots
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(14, 16), sharex=True)

    # TRACK 1: Context (Price + VIX)
    ax1.plot(df.index, df['SPX'], color='#1f77b4', linewidth=1, label='S&P 500 (Log)')
    ax1.set_yscale('log')
    ax1.set_ylabel("S&P 500 Price", color='#1f77b4', fontweight='bold')
    ax1.grid(True, which='both', linestyle='--', alpha=0.3)
    ax1.legend(loc='upper left')
    
    ax1_vix = ax1.twinx()
    ax1_vix.plot(df.index, df['VIX'], color='#9467bd', linewidth=0.8, alpha=0.6, label='VIX')
    ax1_vix.set_ylabel("VIX", color='#9467bd', fontweight='bold')
    ax1_vix.legend(loc='upper right')
    ax1.set_title(f"1. MARKET CONTEXT: Price & VIX", fontsize=10, fontweight='bold', loc='left')

    # TRACK 2: Signal (Alpha Regimes)
    # We plot Climate (2Y) in Teal and Weather (6M) in Orange
    ax2.plot(df.index, df['Alpha_2Y'], color='#008080', linewidth=1.5, label='Climate (2Y Alpha)')
    ax2.plot(df.index, df['Alpha_6M'], color='#ff7f0e', linewidth=1.2, label='Weather (6M Alpha)')
    
    # Critical Thresholds
    ax2.axhline(3.0, color='red', linestyle='--', linewidth=1, label='Extremistan (<3.0)')
    ax2.axhline(4.0, color='green', linestyle='--', linewidth=1, label='Mediocristan (>4.0)')
    
    ax2.set_ylabel("Tail Index (α)")
    ax2.legend(loc='lower left')
    ax2.grid(True, linestyle='--', alpha=0.3)
    ax2.set_title(f"2. SIGNAL ENGINE: Structural Fragility (Alpha)", fontsize=10, fontweight='bold', loc='left')

    # TRACK 3: Pain (Drawdown)
    ax3.fill_between(df.index, df['Drawdown']*100, 0, color='red', alpha=0.3)
    ax3.plot(df.index, df['Drawdown']*100, color='darkred', linewidth=0.5)
    ax3.set_ylabel("Drawdown %")
    ax3.set_ylim(-90, 5) # Scale to fit 1929
    ax3.grid(True, linestyle='--', alpha=0.3)
    ax3.set_title(f"3. PAIN MONITOR: Underwater Plot", fontsize=10, fontweight='bold', loc='left')

    # TRACK 4: Target (Log Returns & Strike Zones)
    # This shows the actual distribution of returns vs the Sigma lines
    ax4.scatter(df.index, df['Log_Return'], s=2, color='gray', alpha=0.4, label='Daily Log Returns')
    
    # Strike Zones (The OTM Puts)
    sigma_5_level = lifetime_mu - (5 * lifetime_sigma)
    sigma_10_level = lifetime_mu - (10 * lifetime_sigma)
    
    ax4.axhline(sigma_5_level, color='orange', linestyle='-', linewidth=1, label='-5σ Strike')
    ax4.axhline(sigma_10_level, color='red', linestyle='-', linewidth=1, label='-10σ Black Swan')
    
    # Annotate the Strike Zones
    ax4.text(df.index[0], sigma_5_level, "  -5σ Strike Zone", color='orange', verticalalignment='bottom', fontsize=8, fontweight='bold')
    ax4.text(df.index[0], sigma_10_level, "  -10σ Black Swan", color='red', verticalalignment='bottom', fontsize=8, fontweight='bold')

    ax4.set_ylabel("Log Return")
    ax4.set_ylim(-0.25, 0.15) # Zoom in on the tails (Cut off the +20% outlier for readability)
    ax4.legend(loc='upper right')
    ax4.grid(True, linestyle='--', alpha=0.3)
    ax4.set_title(f"4. TARGET ACQUISITION: Strike Zones", fontsize=10, fontweight='bold', loc='left')

    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    run_dashboard()

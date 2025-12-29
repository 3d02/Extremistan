import pandas as pd
import matplotlib.pyplot as plt
from typing import Protocol

class Dashboard(Protocol):
    def render(self, df: pd.DataFrame, context: dict):
        ...

class MatplotlibDashboard:
    """
    Renders the 4-track dashboard using Matplotlib.
    """
    def render(self, df: pd.DataFrame, context: dict):
        # Unpack context
        ticker = context.get('ticker', 'Unknown')
        lifetime_mu = context.get('lifetime_mu', 0)
        lifetime_sigma = context.get('lifetime_sigma', 1)

        # Verify columns exist
        required = ['SPX', 'VIX', 'Alpha_2Y', 'Alpha_6M', 'Drawdown', 'Log_Return']
        for col in required:
            if col not in df.columns:
                print(f"Error: Missing column {col} for plotting.")
                return

        # Setup Plot
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
        ax1.set_title(f"1. MARKET CONTEXT: Price & VIX ({ticker})", fontsize=10, fontweight='bold', loc='left')

        # TRACK 2: Signal (Alpha Regimes)
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
        ax3.set_ylim(-90, 5)
        ax3.grid(True, linestyle='--', alpha=0.3)
        ax3.set_title(f"3. PAIN MONITOR: Underwater Plot", fontsize=10, fontweight='bold', loc='left')

        # TRACK 4: Target (Log Returns & Strike Zones)
        ax4.scatter(df.index, df['Log_Return'], s=2, color='gray', alpha=0.4, label='Daily Log Returns')

        # Strike Zones
        sigma_5_level = lifetime_mu - (5 * lifetime_sigma)
        sigma_10_level = lifetime_mu - (10 * lifetime_sigma)

        ax4.axhline(sigma_5_level, color='orange', linestyle='-', linewidth=1, label='-5σ Strike')
        ax4.axhline(sigma_10_level, color='red', linestyle='-', linewidth=1, label='-10σ Black Swan')

        if not df.empty:
            ax4.text(df.index[0], sigma_5_level, "  -5σ Strike Zone", color='orange', verticalalignment='bottom', fontsize=8, fontweight='bold')
            ax4.text(df.index[0], sigma_10_level, "  -10σ Black Swan", color='red', verticalalignment='bottom', fontsize=8, fontweight='bold')

        ax4.set_ylabel("Log Return")
        ax4.set_ylim(-0.25, 0.15)
        ax4.legend(loc='upper right')
        ax4.grid(True, linestyle='--', alpha=0.3)
        ax4.set_title(f"4. TARGET ACQUISITION: Strike Zones", fontsize=10, fontweight='bold', loc='left')

        plt.tight_layout()
        plt.show()

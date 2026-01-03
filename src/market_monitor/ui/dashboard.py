import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from typing import Protocol

class Dashboard(Protocol):
    def render(self, df: pd.DataFrame, context: dict):
        ...

class MatplotlibDashboard:
    """
    Renders the dashboard using Matplotlib.
    Visualizes Raw Log Returns, Outliers, and Drawdown.
    """
    def render(self, df: pd.DataFrame, context: dict):
        # Unpack context
        lifetime_sigma = context.get('lifetime_sigma', 1)
        lifetime_mad = context.get('lifetime_mad', 1)

        # Verify columns exist
        required = ['Log_Return', 'Drawdown', 'SPX', 'VIX', 'Slope']
        for col in required:
            if col not in df.columns:
                print(f"Error: Missing column {col} for plotting.")
                return

        # Setup Plot (4 Tracks)
        # Ratio: 2:2:1:1
        fig, (ax0, ax1, ax2, ax3) = plt.subplots(
            4, 1,
            figsize=(14, 16),
            sharex=True,
            gridspec_kw={'height_ratios': [2, 2, 1, 1]}
        )

        # ---------------------------------------------------------
        # TRACK 1: Macro / Price (SPX Log Scale + VIX)
        # ---------------------------------------------------------
        ax0.set_title("1. MACRO CONTEXT: S&P 500 (Log) & VIX", fontsize=10, fontweight='bold', loc='left')

        # SPX (Left Axis, Log Scale)
        ax0.plot(df.index, df['SPX'], color='black', linewidth=1, label='S&P 500')
        ax0.set_yscale('log')
        ax0.set_ylabel("S&P 500 (Log Scale)")
        ax0.grid(True, which='both', linestyle='--', alpha=0.3)

        # VIX (Right Axis, Linear)
        ax0_right = ax0.twinx()
        ax0_right.plot(df.index, df['VIX'], color='purple', linewidth=0.8, alpha=0.6, label='VIX')
        ax0_right.set_ylabel("VIX", color='purple')
        ax0_right.tick_params(axis='y', labelcolor='purple')

        # Combined Legend
        lines, labels = ax0.get_legend_handles_labels()
        lines2, labels2 = ax0_right.get_legend_handles_labels()
        ax0.legend(lines + lines2, labels + labels2, loc='upper left')

        # ---------------------------------------------------------
        # TRACK 2: Log Returns & Outliers (Dots)
        # ---------------------------------------------------------
        ax1.set_title(f"2. MARKET MONITOR: Returns & Outliers (σ={lifetime_sigma:.4f}, MAD={lifetime_mad:.4f})", fontsize=10, fontweight='bold', loc='left')

        # Define Thresholds
        sigma_5 = 5 * lifetime_sigma
        sigma_10 = 10 * lifetime_sigma
        mad_5 = 5 * lifetime_mad

        # Masks
        mask_10s = df['Log_Return'].abs() > sigma_10
        mask_5s = (df['Log_Return'].abs() > sigma_5) & (~mask_10s)
        mask_5m = (df['Log_Return'].abs() > mad_5) & (~mask_5s) & (~mask_10s)
        mask_normal = ~(mask_10s | mask_5s | mask_5m)

        # Plot Normal (Strike Zone) - Semi-transparent dots
        ax1.scatter(df.index[mask_normal], df['Log_Return'][mask_normal],
                   color='gray', s=10, alpha=0.3, label='Normal')

        # Plot Outliers - Opaque
        ax1.scatter(df.index[mask_5m], df['Log_Return'][mask_5m],
                   color='blue', s=15, alpha=1.0, zorder=3, label='> 5 MAD')
        ax1.scatter(df.index[mask_5s], df['Log_Return'][mask_5s],
                   color='orange', s=20, alpha=1.0, zorder=4, label='> 5σ')
        ax1.scatter(df.index[mask_10s], df['Log_Return'][mask_10s],
                   color='red', s=30, alpha=1.0, zorder=5, label='> 10σ')

        # Reference Lines
        ax1.axhline(sigma_5, color='orange', linestyle='--', linewidth=1, alpha=0.7)
        ax1.axhline(-sigma_5, color='orange', linestyle='--', linewidth=1, alpha=0.7)
        ax1.axhline(sigma_10, color='red', linestyle='-', linewidth=1, alpha=0.7)
        ax1.axhline(-sigma_10, color='red', linestyle='-', linewidth=1, alpha=0.7)
        ax1.axhline(mad_5, color='blue', linestyle=':', linewidth=1, alpha=0.5)
        ax1.axhline(-mad_5, color='blue', linestyle=':', linewidth=1, alpha=0.5)

        # Annotations
        if not df.empty:
            x_min = df.index[0]
            ax1.text(x_min, sigma_5, " +5σ", color='orange', verticalalignment='bottom', fontsize=8, fontweight='bold')
            ax1.text(x_min, -sigma_5, " -5σ", color='orange', verticalalignment='top', fontsize=8, fontweight='bold')
            ax1.text(x_min, sigma_10, " +10σ", color='red', verticalalignment='bottom', fontsize=8, fontweight='bold')
            ax1.text(x_min, -sigma_10, " -10σ", color='red', verticalalignment='top', fontsize=8, fontweight='bold')

        ax1.set_ylabel("Log Return")
        ax1.legend(loc='upper right')
        ax1.grid(True, which='both', linestyle='--', alpha=0.3)

        # ---------------------------------------------------------
        # TRACK 3: Pain Monitor (Drawdown)
        # ---------------------------------------------------------
        ax2.set_title(f"3. PAIN MONITOR: Underwater Plot", fontsize=10, fontweight='bold', loc='left')
        ax2.fill_between(df.index, df['Drawdown']*100, 0, color='red', alpha=0.3)
        ax2.plot(df.index, df['Drawdown']*100, color='darkred', linewidth=0.8)
        ax2.set_ylabel("Drawdown %")
        ax2.set_ylim(bottom=-90, top=5)
        ax2.grid(True, linestyle='--', alpha=0.3)

        # ---------------------------------------------------------
        # TRACK 4: Yield Curve Slope (10Y-3M) - BofA Style
        # ---------------------------------------------------------
        ax3.set_title(f"4. YIELD CURVE: 10Y-3M Slope", fontsize=10, fontweight='bold', loc='left')

        # Zero Line
        ax3.axhline(0, color='black', linewidth=1.5)

        # Main Line
        ax3.plot(df.index, df['Slope'], color='navy', linewidth=1.2, label='10Y-3M')

        # Fill Inversion (Negative)
        # We fill between the curve and 0 where curve < 0
        ax3.fill_between(df.index, df['Slope'], 0, where=(df['Slope'] < 0),
                        color='red', alpha=0.3, interpolate=True, label='Inversion')

        ax3.set_ylabel("Basis Points (%)")
        ax3.grid(True, linestyle='--', alpha=0.3)
        ax3.legend(loc='upper left')

        plt.tight_layout()
        plt.show()

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
        required = ['Log_Return', 'Drawdown']
        for col in required:
            if col not in df.columns:
                print(f"Error: Missing column {col} for plotting.")
                return

        # Setup Plot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 12), sharex=True, gridspec_kw={'height_ratios': [3, 1]})

        # TRACK 1: Log Returns & Outliers
        # Plot Base (Neutral)
        ax1.plot(df.index, df['Log_Return'], color='gray', linewidth=0.5, alpha=0.5, label='Daily Log Returns')

        # Define Thresholds
        sigma_5 = 5 * lifetime_sigma
        sigma_10 = 10 * lifetime_sigma
        mad_5 = 5 * lifetime_mad

        # Highlight Outliers
        # > 10 Sigma (Red)
        mask_10s = df['Log_Return'].abs() > sigma_10
        ax1.scatter(df.index[mask_10s], df['Log_Return'][mask_10s], color='red', s=30, zorder=5, label='> 10σ')

        # > 5 Sigma (Orange) - Exclude 10s to avoid double plot
        mask_5s = (df['Log_Return'].abs() > sigma_5) & (~mask_10s)
        ax1.scatter(df.index[mask_5s], df['Log_Return'][mask_5s], color='orange', s=15, zorder=4, label='> 5σ')

        # > 5 MAD (Blue) - Exclude 5s
        mask_5m = (df['Log_Return'].abs() > mad_5) & (~mask_5s) & (~mask_10s)
        ax1.scatter(df.index[mask_5m], df['Log_Return'][mask_5m], color='blue', s=5, zorder=3, alpha=0.6, label='> 5 MAD')

        # Draw Lines
        # Sigma Lines
        ax1.axhline(sigma_5, color='orange', linestyle='--', linewidth=1, alpha=0.7)
        ax1.axhline(-sigma_5, color='orange', linestyle='--', linewidth=1, alpha=0.7)
        ax1.axhline(sigma_10, color='red', linestyle='-', linewidth=1, alpha=0.7)
        ax1.axhline(-sigma_10, color='red', linestyle='-', linewidth=1, alpha=0.7)

        # MAD Lines
        ax1.axhline(mad_5, color='blue', linestyle=':', linewidth=1, alpha=0.5)
        ax1.axhline(-mad_5, color='blue', linestyle=':', linewidth=1, alpha=0.5)

        # Annotations
        # Only annotate if data exists
        if not df.empty:
            x_min = df.index[0]
            ax1.text(x_min, sigma_5, " +5σ", color='orange', verticalalignment='bottom', fontsize=8, fontweight='bold')
            ax1.text(x_min, -sigma_5, " -5σ", color='orange', verticalalignment='top', fontsize=8, fontweight='bold')
            ax1.text(x_min, sigma_10, " +10σ", color='red', verticalalignment='bottom', fontsize=8, fontweight='bold')
            ax1.text(x_min, -sigma_10, " -10σ", color='red', verticalalignment='top', fontsize=8, fontweight='bold')

        ax1.set_ylabel("Log Return")
        ax1.set_title(f"1. MARKET MONITOR: Returns & Outliers (σ={lifetime_sigma:.4f}, MAD={lifetime_mad:.4f})", fontsize=10, fontweight='bold', loc='left')
        ax1.legend(loc='upper right')
        ax1.grid(True, which='both', linestyle='--', alpha=0.3)

        # TRACK 2: Pain Monitor (Drawdown)
        ax2.fill_between(df.index, df['Drawdown']*100, 0, color='red', alpha=0.3)
        ax2.plot(df.index, df['Drawdown']*100, color='darkred', linewidth=0.8)
        ax2.set_ylabel("Drawdown %")
        ax2.set_ylim(bottom=-90, top=5) # Assuming max drawdown around 86% for SPX historical
        ax2.grid(True, linestyle='--', alpha=0.3)
        ax2.set_title(f"2. PAIN MONITOR: Underwater Plot", fontsize=10, fontweight='bold', loc='left')

        plt.tight_layout()
        plt.show()

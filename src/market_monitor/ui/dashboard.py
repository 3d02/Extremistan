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

        # General Grid & Spine Styling Function
        def style_axis(ax):
            ax.spines[['top', 'right']].set_visible(False)
            ax.grid(True, which='both', linestyle=':', linewidth=0.5, alpha=0.5)
            ax.set_axisbelow(True)

        # ---------------------------------------------------------
        # TRACK 1: Macro / Price (SPX Log Scale + VIX)
        # ---------------------------------------------------------
        ax0.set_title("1. MACRO CONTEXT: S&P 500 (Log) & VIX", fontsize=10, fontweight='bold', loc='left')
        style_axis(ax0)

        # SPX (Left Axis, Log Scale)
        ax0.plot(df.index, df['SPX'], color='black', linewidth=1, label='S&P 500')
        ax0.set_yscale('log')
        ax0.set_ylabel("S&P 500 (Log Scale)")

        # VIX (Right Axis, Linear)
        ax0_right = ax0.twinx()
        ax0_right.spines[['top', 'left']].set_visible(False) # Remove top and left for right axis

        # Create a gradient effect for VIX
        # We simulate a gradient by plotting multiple fill_betweens with decreasing alpha
        # or just a nice solid fill as requested ("switch it to the gradient" - usually implies fill).
        # To be "professional" and robust, a single fill with semi-transparency is best.
        # But let's try to honor "gradient" if simple.
        # Since standard MPL doesn't do gradient fills easily, we will use a solid fill with alpha=0.2
        # which creates a density-like appearance when data is dense, and looks like a background.
        vix_min = df['VIX'].min()
        ax0_right.fill_between(df.index, df['VIX'], vix_min, color='purple', alpha=0.2, label='VIX', zorder=0)

        ax0_right.set_ylabel("VIX", color='purple')
        ax0_right.tick_params(axis='y', labelcolor='purple')

        # Combined Legend
        lines, labels = ax0.get_legend_handles_labels()
        # VIX doesn't have a line, just a fill. We can create a proxy artist or just add it manually.
        # fill_between creates a PolyCollection which is hard to legend automatically sometimes.
        # We'll add a dummy patch for legend.
        import matplotlib.patches as mpatches
        vix_patch = mpatches.Patch(color='purple', alpha=0.2, label='VIX')

        ax0.legend(lines + [vix_patch], labels + ['VIX'], loc='upper left')

        # ---------------------------------------------------------
        # TRACK 2: Log Returns & Outliers (Dots)
        # ---------------------------------------------------------
        ax1.set_title(f"2. MARKET MONITOR: Returns & Outliers (MAD={lifetime_mad:.4f})", fontsize=10, fontweight='bold', loc='left')
        style_axis(ax1)

        # Thresholds
        mad_5 = 5 * lifetime_mad
        mad_7 = 7 * lifetime_mad
        mad_10 = 10 * lifetime_mad

        # Masks
        abs_ret = df['Log_Return'].abs()

        # > 10 MAD
        mask_10_pos = (df['Log_Return'] > mad_10)
        mask_10_neg = (df['Log_Return'] < -mad_10)

        # > 7 MAD (exclusive of 10)
        mask_7_pos = (df['Log_Return'] > mad_7) & (~mask_10_pos)
        mask_7_neg = (df['Log_Return'] < -mad_7) & (~mask_10_neg)

        # > 5 MAD (exclusive of 7 and 10)
        mask_5_pos = (df['Log_Return'] > mad_5) & (~mask_7_pos) & (~mask_10_pos)
        mask_5_neg = (df['Log_Return'] < -mad_5) & (~mask_7_neg) & (~mask_10_neg)

        # Normal
        mask_outliers = mask_10_pos | mask_10_neg | mask_7_pos | mask_7_neg | mask_5_pos | mask_5_neg
        mask_normal = ~mask_outliers

        # Plot Normal (Noise) - Density Cloud
        ax1.scatter(df.index[mask_normal], df['Log_Return'][mask_normal],
                   color='gray', s=1, alpha=0.1, label='Normal', zorder=1)

        # Plot Outliers (Signal)
        # Positive (Blue)
        ax1.scatter(df.index[mask_5_pos], df['Log_Return'][mask_5_pos],
                   color='blue', s=15, alpha=1.0, zorder=3, label='> +5 MAD')
        ax1.scatter(df.index[mask_7_pos], df['Log_Return'][mask_7_pos],
                   color='blue', s=30, alpha=1.0, zorder=4, label='> +7 MAD')
        ax1.scatter(df.index[mask_10_pos], df['Log_Return'][mask_10_pos],
                   color='blue', s=50, alpha=1.0, zorder=5, label='> +10 MAD')

        # Negative (Red)
        ax1.scatter(df.index[mask_5_neg], df['Log_Return'][mask_5_neg],
                   color='red', s=15, alpha=1.0, zorder=3, label='< -5 MAD')
        ax1.scatter(df.index[mask_7_neg], df['Log_Return'][mask_7_neg],
                   color='red', s=30, alpha=1.0, zorder=4, label='< -7 MAD')
        ax1.scatter(df.index[mask_10_neg], df['Log_Return'][mask_10_neg],
                   color='red', s=50, alpha=1.0, zorder=5, label='< -10 MAD')

        # Reference Lines
        for level, color in zip([mad_5, mad_7, mad_10], ['blue', 'blue', 'blue']):
             ax1.axhline(level, color=color, linestyle=':', linewidth=0.5, alpha=0.3)

        for level, color in zip([-mad_5, -mad_7, -mad_10], ['red', 'red', 'red']):
             ax1.axhline(level, color=color, linestyle=':', linewidth=0.5, alpha=0.3)

        # Annotations (Top Left)
        if not df.empty:
            x_min = df.index[0]
            # Just annotate the 10 MAD levels to avoid clutter
            ax1.text(x_min, mad_10, " +10 MAD", color='blue', verticalalignment='bottom', fontsize=8, fontweight='bold')
            ax1.text(x_min, -mad_10, " -10 MAD", color='red', verticalalignment='top', fontsize=8, fontweight='bold')

        ax1.set_ylabel("Log Return")
        # Simplified Legend
        # Create proxy artists for legend to keep it clean
        legend_elements = [
            mpatches.Patch(color='gray', alpha=0.3, label='Normal'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='blue', markersize=8, label='Pos Outlier'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='red', markersize=8, label='Neg Outlier'),
        ]
        ax1.legend(handles=legend_elements, loc='upper right')

        # ---------------------------------------------------------
        # TRACK 3: Pain Monitor (Drawdown)
        # ---------------------------------------------------------
        ax2.set_title(f"3. PAIN MONITOR: Underwater Plot", fontsize=10, fontweight='bold', loc='left')
        style_axis(ax2)

        # Use Red for consistency with Negative Outliers
        ax2.fill_between(df.index, df['Drawdown']*100, 0, color='red', alpha=0.3)
        ax2.plot(df.index, df['Drawdown']*100, color='darkred', linewidth=0.8)
        ax2.set_ylabel("Drawdown %")
        ax2.set_ylim(bottom=-90, top=5)

        # ---------------------------------------------------------
        # TRACK 4: Yield Curve Slope (10Y-3M) - FRED Style
        # ---------------------------------------------------------
        ax3.set_title(f"4. YIELD CURVE: 10Y-3M Slope", fontsize=10, fontweight='bold', loc='left')
        style_axis(ax3)

        # Zero Line
        ax3.axhline(0, color='black', linewidth=1.0, alpha=0.5)

        # Recession Shading
        if 'Recession' in df.columns:
            # We shade regions where Recession == 1
            # transform=ax3.get_xaxis_transform() allows us to shade full height (y=0 to 1 in axes coords)
            ax3.fill_between(df.index, 0, 1, where=(df['Recession'] == 1),
                            color='#e0e0e0', alpha=0.5, transform=ax3.get_xaxis_transform(),
                            label='Recession', zorder=0)

        # Main Line (FRED Blue)
        ax3.plot(df.index, df['Slope'], color='#4572A7', linewidth=1.5, label='10Y-3M')

        # No Fill for Inversion (Removed per request)

        ax3.set_ylabel("Percent")
        # Adjust legend to include Recession if present
        # We manually construct legend handles to ensure cleanliness
        handles, labels = ax3.get_legend_handles_labels()
        # Filter duplicates if any
        by_label = dict(zip(labels, handles))
        ax3.legend(by_label.values(), by_label.keys(), loc='upper left')

        plt.tight_layout()
        plt.show()

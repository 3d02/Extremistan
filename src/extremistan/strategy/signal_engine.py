import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Literal

SignalType = Literal["GO", "NO-GO", "WATCH", "CAUTION"]

@dataclass
class SignalResult:
    signal: SignalType
    alpha_2y: float
    alpha_6m: float
    description: str

class SignalEngine:
    """
    Evaluates market regime based on Hill Estimator Alphas and Cross-Asset Stress.
    Rules:
    - Alpha 2Y < 3.0: Extremistan (Fat Tails)
    - If Fragility Density > 50%:
        - Check Cross-Asset (Slope Inversion or High MOVE) for High Conviction GO.
        - Otherwise GO (Standard).
    - If Healing Density > 50%: Downgrade to WATCH.
    """

    def __init__(self, extremistan_threshold: float = 3.0, caution_threshold: float = 3.5):
        self.extremistan_threshold = extremistan_threshold
        self.caution_threshold = caution_threshold

    def evaluate(self,
                 alpha_2y: float,
                 alpha_6m: float,
                 fragility_density: float = 0.0,
                 healing_density: float = 0.0,
                 slope: float = np.nan,
                 move_index: float = np.nan,
                 vol_stress: float = np.nan) -> SignalResult:
        """
        Evaluates the strategic signal.

        Args:
            alpha_2y: The 2-Year Climate Hill Alpha.
            alpha_6m: The 6-Month Weather Hill Alpha.
            fragility_density: The percentage of days in the last 20 days where Weather < Climate (0.0 to 1.0).
            healing_density: The percentage of days in the last 20 days where Weather > Climate (0.0 to 1.0).
            slope: Term Structure Slope (10Y - Short Rate). Negative implies inversion.
            move_index: Bond Volatility Index. High levels (>120) indicate stress.
            vol_stress: Z-Score of current return vs regime volatility.
        """
        if pd.isna(alpha_2y):
             return SignalResult("NO-GO", alpha_2y, alpha_6m, "Insufficient Data (Climate)")

        signal: SignalType = "NO-GO"
        description = "Neutral/Safe"

        # Handle NaNs for optional inputs
        fragility_density = fragility_density if not pd.isna(fragility_density) else 0.0
        healing_density = healing_density if not pd.isna(healing_density) else 0.0
        slope = slope if not pd.isna(slope) else 999.0 # Default to positive slope (safe)
        move_index = move_index if not pd.isna(move_index) else 0.0

        is_extremistan = alpha_2y < self.extremistan_threshold
        is_caution = alpha_2y < self.caution_threshold

        # Cross-Asset Stress Flags
        is_slope_inverted = slope < 0
        is_move_stress = move_index > 120 # Arbitrary high stress level, can be tuned
        is_cross_asset_stress = is_slope_inverted or is_move_stress

        if is_extremistan:
            if fragility_density > 0.5:
                if is_cross_asset_stress:
                    signal = "GO"
                    description = f"HIGH CONVICTION (Density {fragility_density:.0%} + Macro Stress)"
                else:
                    signal = "GO"
                    description = f"Fragile Regime (Density {fragility_density:.0%})"

                # Healing Logic: If healing density is high, we might downgrade or exit
                # "Add a healing density... to exit or downgrade a GO"
                if healing_density > 0.5:
                    signal = "WATCH"
                    description = f"Healing Detected (Density {healing_density:.0%})"
            else:
                signal = "WATCH"
                description = f"Structural Fragility - Wait for Density > 50% (Curr: {fragility_density:.0%})"

        elif is_caution:
            if is_cross_asset_stress:
                signal = "CAUTION"
                description = "Warning Zone + Macro Stress"
            else:
                signal = "CAUTION"
                description = "Warning Zone"

        return SignalResult(signal, alpha_2y, alpha_6m, description)

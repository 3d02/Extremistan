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
    Evaluates market regime based on Hill Estimator Alphas.
    Rules:
    - Alpha 2Y < 3.0: Extremistan (Fat Tails)
    - If Alpha 6M < Alpha 2Y: Fragilizing -> GO
    - Else: Healing -> WATCH
    """

    def __init__(self, extremistan_threshold: float = 3.0, caution_threshold: float = 3.5):
        self.extremistan_threshold = extremistan_threshold
        self.caution_threshold = caution_threshold

    def evaluate(self, alpha_2y: float, alpha_6m: float, fragility_density: float = 0.0) -> SignalResult:
        """
        Evaluates the strategic signal.

        Args:
            alpha_2y: The 2-Year Climate Hill Alpha.
            alpha_6m: The 6-Month Weather Hill Alpha.
            fragility_density: The percentage of days in the last 20 days where Weather < Climate (0.0 to 1.0).
        """
        # Note: We allow alpha_6m to be NaN because sparse data is expected now.
        # But for 'Climate' (2Y), we generally expect it to be stable.
        if pd.isna(alpha_2y):
             return SignalResult("NO-GO", alpha_2y, alpha_6m, "Insufficient Data (Climate)")

        signal: SignalType = "NO-GO"
        description = "Neutral/Safe"

        if alpha_2y < self.extremistan_threshold:
            # New Rule: Density of Fragility > 50%
            # If density is NaN, treat as 0
            density = fragility_density if not pd.isna(fragility_density) else 0.0

            if density > 0.5:
                signal = "GO"
                description = f"High Conviction (Density {density:.0%})"
            else:
                signal = "WATCH"
                description = f"Structural Fragility - Wait for Density > 50% (Curr: {density:.0%})"
        elif alpha_2y < self.caution_threshold:
            signal = "CAUTION"
            description = "Warning Zone"

        return SignalResult(signal, alpha_2y, alpha_6m, description)

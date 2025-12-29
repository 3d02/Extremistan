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

    def evaluate(self, alpha_2y: float, alpha_6m: float) -> SignalResult:
        if pd.isna(alpha_2y) or pd.isna(alpha_6m):
             return SignalResult("NO-GO", alpha_2y, alpha_6m, "Insufficient Data")

        signal: SignalType = "NO-GO"
        description = "Neutral/Safe"

        if alpha_2y < self.extremistan_threshold:
            if alpha_6m < alpha_2y:
                signal = "GO"
                description = "High Conviction Extremistan"
            else:
                signal = "WATCH"
                description = "Structural Fragility - Wait for local crack"
        elif alpha_2y < self.caution_threshold:
            signal = "CAUTION"
            description = "Warning Zone"

        return SignalResult(signal, alpha_2y, alpha_6m, description)

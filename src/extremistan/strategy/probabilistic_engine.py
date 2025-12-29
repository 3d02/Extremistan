import pandas as pd
import numpy as np
from typing import List, Dict, Tuple
from dataclasses import dataclass

@dataclass
class ProbabilityResult:
    maturity: str
    strike_otm_pct: float
    probability_itm: float
    avg_return_multiple: float # Optional: Average (Payoff / Cost) if we had option pricing, or just Payoff/0?
                               # Since we don't have option prices, we can't calculate ROI.
                               # We will just stick to ITM Probability for now as requested.

class ProbabilisticEngine:
    """
    Evaluates market regime using Nearest Neighbor Search on historical "State of the World" vectors.
    Calculates probability of OTM puts landing ITM based on future returns of matched historical days.
    """

    def __init__(self, feature_matrix: pd.DataFrame):
        self.history = feature_matrix.copy()
        # Features to use for distance calculation
        self.features = ['Alpha_2Y', 'Alpha_6M', 'Slope', 'VIX', 'VIX_Curve', 'SKEW']

        # Standardize history (Z-Score) for fair distance calculation
        # We calculate mean/std from the WHOLE history provided.
        # In a strict backtest, this is look-ahead bias.
        # But for "Regime Similarity" we often want to know "where does today sit in the global context".
        # If the user wants strictly point-in-time, we would standardize based on expanding window.
        # Given "Option A: Nearest Neighbor", usually implies global context or expanding.
        # We'll use global context of the loaded history as the "Universe of Knowledge".
        self.means = self.history[self.features].mean()
        self.stds = self.history[self.features].std()

        self.norm_history = (self.history[self.features] - self.means) / self.stds

    def find_similar_regimes(self, current_vector: pd.Series, n_neighbors: int = 50) -> pd.DatetimeIndex:
        """
        Finds top N historical dates with smallest Euclidean distance to current_vector.
        """
        # Normalize current vector using historical stats
        norm_current = (current_vector[self.features] - self.means) / self.stds

        # Calculate Euclidean distance
        # dist = sqrt(sum((x - y)^2))
        diff = self.norm_history - norm_current
        sq_diff = diff ** 2
        distances = np.sqrt(sq_diff.sum(axis=1))

        # Sort and take top N
        # We must exclude the current date if it exists in history (to avoid self-match)
        # Assuming current_vector is "today" and might not be in history yet, or if it is, distance is 0.
        # We'll just sort. If dist is 0, it means it's the same day (or identical).
        # Usually we want past similar days, not today.

        # If current_date is in index, drop it
        if current_vector.name in distances.index:
             distances = distances.drop(current_vector.name)

        nearest = distances.nsmallest(n_neighbors)
        return nearest.index

    def calculate_probabilities(self,
                                matched_dates: pd.DatetimeIndex,
                                maturities_months: List[int] = [1, 2, 3, 4, 5, 6],
                                otm_strikes_pct: List[float] = [0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50]) -> pd.DataFrame:
        """
        Calculates P(ITM) for grid of maturities and OTM strikes.

        Logic:
        For each matched date 't':
          For each maturity 'm' (convert to trading days, approx m*21):
             Future Price P_{t+m}
             Strike K = P_t * (1 - OTM%)
             If P_{t+m} < K, then ITM.

        Probability = Count(ITM) / Total Matches
        """

        results = {}

        # Approximate trading days per month
        days_per_month = 21

        total_matches = len(matched_dates)
        if total_matches == 0:
            return pd.DataFrame()

        for m in maturities_months:
            days_forward = m * days_per_month
            col_name = f"{m}M"
            results[col_name] = []

            # Vectorized check for this maturity
            # We need P_t and P_{t+m} for all matched dates

            # Get P_t
            # self.history has 'SPX'.
            p_t = self.history.loc[matched_dates, 'SPX']

            # Get P_{t+m}
            # We need to find the index integer location, shift by days_forward, check validity
            # This is tricky with DatetimeIndex if we use calendar days.
            # We should use integer indexing into the full dataframe.

            # Map matched dates to integer indices in self.history
            # We need the full history to look forward
            full_idx = self.history.index

            # We can use searchsorted or just map if exact match
            # But simpler: get integer locations of matched_dates
            # Since matched_dates is a subset of history index (guaranteed by find_similar_regimes logic)

            # Get integer locations
            # Explicitly finding index in the unique sorted index of history
            inds = [self.history.index.get_loc(d) for d in matched_dates]
            inds_forward = [i + days_forward for i in inds]

            # Filter out indices that go beyond available history
            valid_pairs = []
            for i, i_fwd in zip(inds, inds_forward):
                if i_fwd < len(self.history):
                    valid_pairs.append((i, i_fwd))

            if not valid_pairs:
                # If all matches are too recent to have a future, return NaNs or 0
                for _ in otm_strikes_pct:
                    results[col_name].append(np.nan)
                continue

            idx_t, idx_fwd = zip(*valid_pairs)

            price_t = self.history.iloc[list(idx_t)]['SPX'].values
            price_fwd = self.history.iloc[list(idx_fwd)]['SPX'].values

            # Calculate Max Drawdown in the window?
            # The prompt asks: "option ends In-The-Money (ITM) at maturity".
            # So strictly P_{t+m} < Strike.
            # It does NOT ask if it touched ITM (barrier).
            # "1. option ends In-The-Money (ITM) at maturity" -> Confirmed.

            # Calculate probabilities for each strike
            probs = []
            for otm in otm_strikes_pct:
                # Strike K = P_t * (1 - otm)
                strike = price_t * (1.0 - otm)

                # Check ITM: Price_fwd < Strike
                is_itm = price_fwd < strike

                prob = np.sum(is_itm) / len(valid_pairs)
                probs.append(prob)

            results[col_name] = probs

        # Construct DataFrame
        # Index: OTM %
        # Columns: Maturities
        df_probs = pd.DataFrame(results, index=[f"{int(otm*100)}%" for otm in otm_strikes_pct])

        return df_probs

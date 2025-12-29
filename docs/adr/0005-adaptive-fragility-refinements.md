# ADR 0005: Adaptive Fragility Refinements

## Status
Accepted

## Context
The previous "Weather Alpha" implementation (ADR 0004) used weekly resampling to reduce noise but introduced significant small-sample bias ($k \approx 5$) and a "Ghost Effect" where outliers locked the signal for 6 months. Additionally, the cross-asset stress triggers lacked sensitivity to *acute* changes (Rate of Change), and the execution logic was not strictly aligned with T-1 data availability for pre-market decision making.

## Decision
We have refined the fragility engine with the following changes:

1.  **Daily Resolution for Weather Alpha:** Abandon weekly resampling. Calculate `Alpha_6M` on daily data using a 126-day rolling window. This increases $n$ to ~126, yielding $k \approx 11$, significantly stabilizing the tail estimator variance.
2.  **Momentum Healing:** Introduce `Alpha_6M_ROC` (10-day Rate of Change). If `Alpha_6M` improves by >5% in 10 days, the engine considers this a "Healing" signal, allowing for an earlier downgrade to WATCH even if the level is still below Climate Alpha. This directly counters the "Ghost Effect".
3.  **Acute Cross-Asset Stress:** Introduce `MOVE_ROC` (5-day Rate of Change). If Bond Volatility spikes by >10% in 5 days, the "High Conviction" GO signal is triggered, even if the absolute MOVE level is below 120. This captures rapid systemic deterioration.
4.  **Strict T-1 Data Execution:** The live signal generation now explicitly uses the last available close (`iloc[-1]`) of the *unshifted* data columns. This ensures the decision is made on the most recent complete dataset (yesterday's close) without introducing artificial lag or look-ahead bias.

## Consequences
*   **Positives:**
    *   **Statistical Stability:** Higher $k$ reduces the standard error of the Hill Estimator.
    *   **Responsiveness:** Acute ROC triggers allow the system to react to fast-moving crashes before absolute levels become critical.
    *   **Nuance:** Momentum healing prevents capital from being trapped in "GO" mode solely due to stale outliers.
    *   **Precision:** Strict T-1 logic aligns the code with real-world trading operations.
*   **Negatives:**
    *   **Daily Noise:** Moving to daily resolution might reintroduce some short-term noise, though the adaptive $k$ helps mitigate this.
    *   **Complexity:** The signal logic now has more state (ROCs) and conditional paths.

## Alternatives Considered
*   **Exponential Decay:** We considered exponentially weighting the Hill input, but it mathematically conflicts with the standard definition of the estimator. ROC provides a clearer "derivative-based" exit.
*   **Intraday Data:** Rejected for now; the system remains End-of-Day (EOD) based to filter out intraday noise.

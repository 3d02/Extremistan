# ADR 0004: Adaptive Tail Estimation and Cross-Asset Signals

## Status
Accepted

## Context
The previous implementation of the Hill Estimator used a fixed percentage of tail observations (`k_pct`) or a static minimum (`min_k`). This approach was sensitive to window length and clustered extremes, leading to unstable variance. Additionally, the signal logic relied solely on equity market fragility, ignoring cross-asset stress signals like yield curve inversion or bond volatility, and lacked a mechanism to confirm "healing" after a crash.

## Decision
We have decided to:
1.  **Adopt Adaptive Tail Sizing:** Use the Danielsson–de Vries heuristic `k = max(min_k, int(sqrt(n)))` for Hill Estimator calculation. This stabilizes variance by adapting the tail fraction to the sample size.
2.  **Implement Weekly Resampling:** Calculate the "Weather" (6-month) Alpha on weekly data to reduce autocorrelation with the "Climate" (2-year) Alpha and capture different frequency dynamics.
3.  **Integrate Cross-Asset Signals:** Incorporate Term Structure Slope (10Y - 3M) and MOVE Index (Bond Volatility) as confirmation filters for the strategic signal.
4.  **Symmetric Persistence Logic:** Introduce "Healing Density" (frequency of Weather > Climate) to explicitly downgrade signals when fragility dissipates.
5.  **Enforce Backtesting Hygiene:** Apply a 1-day lag (`shift(1)`) to all strategic indicators before signal evaluation to strictly prevent look-ahead bias.

## Consequences
*   **Positives:**
    *   More robust tail estimation that adapts to volatility regimes.
    *   Reduced false positives by requiring persistence and potentially cross-asset confirmation.
    *   Clearer exit signals via the Healing Density metric.
    *   Elimination of look-ahead bias in backtests.
*   **Negatives:**
    *   Weekly resampling reduces the number of observations for the 6-month window, potentially making the Hill estimator noisier if the window has very few negative returns.
    *   Increased data dependency (requires Treasury yields and MOVE index).

## Alternatives Considered
*   **Fixed `k` with larger windows:** Rejected because it doesn't solve the issue of clustered extremes and ignores the dynamic nature of tail thickness.
*   **Pure Equity Signals:** Rejected because macro factors (rates, funding) often lead equity stress, and ignoring them reduces the robustness of the "Extremistan" detection.

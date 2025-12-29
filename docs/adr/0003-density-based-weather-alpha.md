# ADR-0003: Switch to Density-Based Signal for Weather Alpha

## Status
Accepted

## Context
The "Weather Alpha" (6-Month Hill Estimator) is designed to detect local, high-frequency shifts in tail fatness. However, a 6-month window often lacks enough tail observations (top 5% of losses) to satisfy a strict Hill Estimator, leading to frequent `NaN` values or noise.

When visualized as a continuous line, these sparse data points create a misleading impression of a continuous trend (the "Line Trap"). Furthermore, the previous strategic rule—a simple geometric crossover where Weather Alpha drops below Climate Alpha—is prone to "False Positives" caused by single, noisy calculations.

## Decision
We define a new "Honest Statistician's" approach:
1.  **Visualization:** We will display the Weather Alpha as **discrete points** (`ax.scatter`) rather than a line. This visually acknowledges that each estimation is a discrete event based on a sparse sample.
2.  **Strategic Logic:** We switch from a simple "Crossover" rule to a **"Fragility Persistence" (Density)** rule.
    *   We calculate `is_fragile` for every valid point where Weather Alpha < Climate Alpha.
    *   We track the density of these events over a rolling 20-day window.
    *   **GO Signal:** Triggered only when the density of fragility events > 50% (i.e., fragility is persistent, not a one-off noise).

## Consequences

### Positive
*   **Reduced False Positives:** The density rule filters out transient noise, ensuring we only trade when structural fragility is persistent.
*   **Intellectual Honesty:** The point plot visualization accurately represents the sparse nature of the data, preventing the strategist from seeing trends that don't exist.
*   **Adaptive Thresholding:** We accept a lower Minimum $k$ ($k \ge 4$) for the 6-month window to get *some* data, but rely on the Density Rule to filter the increased noise.

### Negative
*   **Lag:** The density check introduces a slight lag compared to an instantaneous crossover, potentially missing the absolute bottom of a crash onset (though "catching a falling knife" is not the goal).
*   **Complexity:** The mental model moves from "Line A crosses Line B" to "Cluster density exceeds Threshold," which is slightly harder to visualize instantly without the dashboard aid.

## Alternatives Considered
*   **Heavily Dotted Line:** Still implies connectivity between temporally distant points.
*   **Interpolation:** Filling the gaps with linear interpolation was rejected as it fabricates data where none exists.

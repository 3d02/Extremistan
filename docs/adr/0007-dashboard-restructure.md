# ADR-0007: Dashboard Visualization Restructure

## Status
Accepted

## Context
The user requested a significant update to the Market Monitor dashboard to better visualize macro context, outlier events, and yield curve signals. The previous dashboard only showed log returns and drawdown. The user specifically requested:
1.  Dots instead of lines for log returns to better visualize discrete daily events.
2.  A new subplot for S&P 500 (Log Scale) overlaid with VIX.
3.  A new subplot for the 10Y-3M Yield Curve Slope (BofA style).
4.  Refactoring of code to adhere to `AGENTS.md` rules (logging vs print).

## Decision
We have restructured the `MatplotlibDashboard` to include 4 vertical tracks (subplots):
1.  **Macro Context**: S&P 500 Price (Log Scale, Left Axis) and VIX (Linear, Right Axis). This provides high-level market context.
2.  **Market Monitor**: Log Returns plotted as semi-transparent dots for normal days, with opaque colored dots for outliers (>5σ, >10σ, >5 MAD). This highlights tail events more clearly than a line chart.
3.  **Pain Monitor**: Drawdown (Underwater plot). Unchanged.
4.  **Yield Curve**: 10Y-3M Slope with a zero line and red fill for negative values (inversion).

We also refactored `main.py` to:
- Move data management logic to `market_monitor.data.manager`.
- Move text reporting logic to `market_monitor.ui.reporter`.
- Use `logging` for operational messages and `print` only for the final human-readable report.

## Consequences
### Positive
*   **Enhanced Insight**: The new dashboard provides a comprehensive view of price, volatility, tail risk, and macro signals in a single view.
*   **Better Outlier Visualization**: Dots make it easier to see clustering and frequency of outlier events without the noise of connecting lines.
*   **Code Cleanliness**: Refactoring improves separation of concerns and adherence to project governance.

### Negative
*   **Complexity**: The dashboard code is now more complex with 4 subplots and dual-axis logic.
*   **Screen Real Estate**: 4 vertical subplots require a taller figure size to remain readable.

## Alternatives Considered
*   **Separate Windows**: We considered opening multiple figures, but a single dashboard is preferred for a "cockpit" view.
*   **Interactive Web Dashboard**: Moving to Plotly/Dash was considered but out of scope for this specific task which targeted the existing Matplotlib implementation.

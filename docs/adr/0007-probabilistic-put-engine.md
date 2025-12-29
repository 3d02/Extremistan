# ADR 0007: Probabilistic Put Engine

## Status
Accepted

## Context
The previous `SignalEngine` provided discrete signals ("GO", "WATCH", "NO-GO") based on rule-based thresholds of Hill Estimator Alphas and cross-asset stress. While useful for binary decision making, it lacked the granularity required to assess specific option strategies. The user requested a system to "understand if we are in the right window to buy OTM puts" by assessing the probability of puts landing ITM across various maturities and OTM percentages.

This requires a shift from discrete rules to a probabilistic "Regime Similarity" approach.

## Decision
We implemented a `ProbabilisticEngine` that:
1.  Constructs a "State of the World" vector using:
    *   Hill Alphas (Climate 2Y, Weather 6M)
    *   Yield Curve Slope (10Y - 3M)
    *   VIX Level
    *   VIX Term Structure (VIX / VIX3M)
    *   SKEW Index
2.  Uses **Nearest Neighbor Search** (Euclidean distance on Z-Scored features) to find the $N$ most similar historical days.
3.  Calculates the probability of OTM puts (20-50% OTM, 3-6M maturity) landing ITM by observing the actual forward returns of the S&P 500 from those matched historical dates.
4.  Outputs a 2D probability table (Maturity vs OTM %) to the console.

We also updated the data ingestion pipeline (`RegimeAnalytics`) to support the new indicators (`^VIX3M`, `^SKEW`) and ensure strict T-1 alignment (preventing look-ahead bias).

## Consequences
*   **Positive:**
    *   Provides actionable, granular probabilities for option selection.
    *   Data-driven "Regime Similarity" is less brittle than hard-coded thresholds.
    *   Incorporates implied volatility surface information (Skew, Term Structure).
*   **Negative:**
    *   Computationally heavier (requires full history processing for rolling alphas).
    *   Depends on the availability of long history for indicators like `VIX3M` (starts 2006) and `SKEW` (starts 1990), limiting the effective backtest window compared to pure price data (1927+).

## Alternatives Considered
*   **Black-Scholes Probability:** rejected as explicitly requested by the user ("Never use Black–Scholes model - it is not usable for fat tails approach").
*   **Discrete Bucketing:** rejected in favor of Nearest Neighbor for better handling of continuous multi-dimensional data.

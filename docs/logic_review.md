# Logic Review and Improvement Plan

## Observed Architecture and Signal Flow
* **Data ingestion:** Yahoo Finance adapter with Parquet caching; CSV adapter for offline workflows. Both normalize into a simple price panel before analytics.
* **Analytics core:** Log returns, Hill tail-index estimation over two rolling windows (2Y *Climate* vs. 6M *Weather*), drawdown computation, and lifetime distribution estimates.
* **Signal engine:** Categorical regime detection driven by (1) `Alpha_2Y` extremistan threshold (`<3.0`), (2) comparative `Alpha_6M` fragility, and (3) a 20-day fragility-density filter requiring >50% persistence for a “GO.”
* **Visualization:** Matplotlib dashboard summarizing price, VIX, alphas, drawdowns, and sigma-strike scatter.

## Scrutiny of Current Logic
* **Tail-index stability:** Fixed `k_pct` (5%/10%) with static `min_k` makes the Hill estimator sensitive to window length and clustered extremes. Variance of the estimator can explode when the loss count barely clears `min_k`.
* **Window orthogonality:** Using 504 vs. 126 trading days creates a four-to-one ratio, but both windows fully overlap. This inflates correlation between *Climate* and *Weather*, muting the fragility density’s discriminative power.
* **Volatility normalization:** Lifetime sigma anchors the sigma-strike plot, but it ignores non-stationarity; post-1987 volatility regimes dominate the distribution, biasing sigma cutoffs for early-period data.
* **Signal asymmetry:** Fragility density is only triggered when `Alpha_6M < Alpha_2Y`, but there is no complementary healing density to confirm exits or suppress false positives after a crash.
* **Macro covariance gaps:** The logic is univariate on SPX with a passive VIX readout; it ignores cross-asset stress (rates, credit spreads, USD funding) that often lead equity fragility.

## Improvement Recommendations
1. **Adaptive tail sizing**
   * Dynamically choose `k` via the Danielsson–de Vries heuristic (`k ≈ n^{0.5}` capped by a stability band) to stabilize variance during calm periods while still capturing deep tails during stress.
   * Add a Hill plot diagnostic and monitor slope monotonicity to catch regions where Pareto assumptions break.
2. **Overlap-controlled windows**
   * Shift *Weather* to a shorter, semi-overlapping span (e.g., 3M or 4M) or compute it on weekly bars to lower autocorrelation with *Climate*.
   * Track the rolling correlation between `Alpha_2Y` and `Alpha_6M`; gate the fragility density when correlation exceeds a ceiling (e.g., 0.85).
3. **Regime-aware normalization**
   * Replace lifetime sigma with a rolling long-horizon volatility proxy (e.g., 5Y EWMA) for sigma-strike zones, and annotate z-scores against both lifetime and regime-adjusted sigma to surface regime shifts.
4. **Symmetric persistence logic**
   * Add a healing density (`Alpha_6M > Alpha_2Y`) to exit or downgrade a GO when fragility is dissipating, reducing path-dependency after large shocks.
   * Consider Bayesian updating on fragility density (Beta-Binomial) to de-emphasize short-lived clusters of points.
5. **Cross-asset stress overlays**
   * Incorporate term-structure signals (e.g., 2s10s slope, FRA-OIS, MOVE index) as secondary filters; require either equity fragility + rates stress or widen drawdown risk bands when credit/funding spreads spike.
6. **Backtesting hygiene**
   * Enforce a look-ahead buffer in rolling computations (`shift(1)`) before signal evaluation to prevent peeking.
   * Use block bootstrapping for drawdown and fragility-density confidence intervals to quantify the reliability of alerts across regimes.

## Execution Framework (Pythonic Sketch)
```python
def adaptive_hill_alpha(returns: pd.Series, min_k: int = 10) -> float:
    losses = -returns[returns < 0].dropna()
    n = len(losses)
    if n < min_k:
        return np.nan

    k = max(min_k, int(np.sqrt(n)))
    threshold = np.partition(losses.values, -k)[-k]
    top_k = losses[losses >= threshold]
    xi = np.mean(np.log(top_k / threshold))
    return 1.0 / xi if xi > 0 else np.nan
```

## Risk Assessment
* **Estimator misspecification:** Hill assumes Pareto tails; structural breaks (e.g., circuit breakers post-1987) violate i.i.d. tails, leading to understated fragility.
* **Parameter overfitting:** Tuning `k`, window sizes, or density thresholds on a single market regime risks inflating Sharpe through data snooping; parameter sweeps must be nested inside an out-of-sample validation loop.
* **Data latency and quality:** Yahoo Finance adjustments can shift historical prices; caching layer should record the data version/hash to detect silent upstream revisions that would change alpha trajectories.

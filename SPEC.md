# Project Extremistan: Specification & Guardrails

## 1. Core Assumptions

### 1.1 Market Physics (The "Extremistan" Hypothesis)
*   **Non-Gaussian Distribution:** Financial returns do not follow a Normal (Gaussian) distribution. They exhibit high Kurtosis (fat tails) and Power-Law decay.
*   **Scale Invariance:** The mechanism causing a 5% drop is structurally similar to the mechanism causing a 20% crash, just at a different scale.
*   **Infinite Variance Potential:** In certain regimes (Tail Index $\alpha \to 2.0$), the variance of the market becomes theoretically undefined/infinite, rendering standard risk models (VaR, Sharpe Ratio) useless.

### 1.2 Mathematical Framework
*   **Logarithmic Returns:** We assume continuously compounded log returns ($r_t = \ln(P_t / P_{t-1})$) are the correct unit of analysis because they are time-additive and normalize the price series for statistical operations.
*   **Hill Estimator Efficacy:** We assume the Hill Estimator is a valid estimator for the Tail Index ($\alpha$) of the return distribution's Power-Law tail, provided $k$ (tail sample size) is chosen correctly (top 5% of losses).
*   **Stationarity of Windows:** We assume that over the chosen rolling windows (2-Year "Climate", 6-Month "Weather"), the statistical properties of the tail are sufficiently stationary to yield a meaningful signal.

### 1.3 Strategic Logic
*   **Ghost Effect:** A low 2-year Alpha (high risk) might be a lag artifact from a crash 18 months ago. Comparing it to the 6-month Alpha allows us to distinguish between "healing" markets and "deteriorating" markets.
*   **Fragility Persistence (Density Rule):** Unlike simple crossover signals which can be noisy, we require "Fragility Persistence." A GO signal triggers only when the Weather Alpha (< 6M) has been structurally below the Climate Alpha (> 2Y) for a significant density (> 50%) of the recent 20-day window.
*   **Regime Divergence:** The most profitable trades occur when implied volatility (VIX) is low (market is complacent) but structural fragility (Hill Alpha) is high.

---

## 2. Backtest Guardrails & Anti-Bias Rules

### 2.1 No Look-Ahead Bias
*   **Strict Windowing:** All signals must be calculated using *only* data available up to time $t$. The rolling window calculations (`rolling(window=...)`) naturally enforce this, but any future modifications must explicitly verify that no $t+1$ data leaks into the decision at time $t$.
*   **Lagged Execution:** If a signal is generated at the Close of day $t$, the execution price is assumed to be the *next* available price (Open or Close of $t+1$), or the Close of $t$ if and only if the system is designed for "Market On Close" (MOC) execution.

### 2.2 Data Integrity
*   **Survivorship Bias:** While the S&P 500 index itself suffers from survivorship bias (constituents are added/removed), the *index level* is a continuous time series representing the aggregate market. We accept the index-level bias as a feature of the instrument (SPY/SPX).
*   **Data Quality Checks:**
    *   Missing data points must be filled (forward-fill) or dropped explicitly.
    *   Zeros or negative prices (in raw data) must be treated as errors.

### 2.3 Overfitting Prevention
*   **Parameter Stability:** The choice of window sizes (504 days, 126 days) and $k$ threshold (5%) should not be optimized to fit a specific crash (e.g., 2008). They must be robust across multiple decades (1929, 1987, 2000, 2020).
*   **Regime Robustness:** The strategy must be tested across different volatility regimes (low vol 2017 vs. high vol 2008).

### 2.4 Transaction Costs & Friction
*   **Execution Slippage:** Backtests must assume non-zero slippage, especially during high-volatility events where liquidity dries up.
*   **Cost of Carry:** The "Bleed" from long OTM options is the primary cost. Simulations must account for Theta decay and not just directional PnL.

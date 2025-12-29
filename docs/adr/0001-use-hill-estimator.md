# ADR-0001: Use of Hill Estimator for Tail Risk

## Status
Accepted

## Context
Financial markets exhibit "fat tails" (high Kurtosis), meaning extreme events occur far more frequently than predicted by the Normal Distribution. Standard deviation ($\sigma$) is an inadequate metric for risk in these environments because it assumes a finite variance and a Gaussian bell curve. We needed a metric that explicitly measures the "fatness" of the tail—the rate at which the probability of extreme losses decays.

## Decision
We decided to use the **Hill Estimator** to calculate the Tail Index ($\alpha$) of the return distribution.

The Hill Estimator is defined as:
$$ \alpha = \left[ \frac{1}{k} \sum_{i=1}^{k} \ln\left(\frac{L_{(i)}}{L_{(k+1)}}\right) \right]^{-1} $$

Where we focus on the top $k$ percent (typically 5%) of the worst losses.

## Consequences

### Positive
*   **Power-Law Sensitivity:** The Hill Estimator is specifically designed for Power-Law distributions, making it ideal for "Extremistan" markets.
*   **Regime Detection:** It provides a clear numerical signal. An $\alpha$ dropping towards 2.0 signals theoretically infinite variance (instability), whereas an $\alpha > 4.0$ signals a safe, Gaussian-like environment.

### Negative
*   **Data Hungry:** The estimator requires a significant sample size in the tail to be stable. This forces us to use long rolling windows (2 years = 504 days) to get enough tail data points.
*   **Threshold Sensitivity:** The results are sensitive to the choice of $k$ (the threshold between the "body" and the "tail").
*   **Bias:** It is known to be biased for small samples, though it is asymptotically consistent.

## Alternatives Considered
*   **Kurtosis:** While easier to calculate, Kurtosis is a single moment that doesn't describe the *shape* of the decay as precisely as the Tail Index.
*   **VaR (Value at Risk):** VaR measures a threshold loss at a confidence level but says nothing about *how bad* things can get beyond that threshold.

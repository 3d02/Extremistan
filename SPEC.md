# Market Monitor: Specification & Guardrails

## 1. Core Assumptions

### 1.1 Market Physics (The "Fat Tails" Hypothesis)
*   **Non-Gaussian Distribution:** Financial returns do not follow a Normal (Gaussian) distribution. They exhibit high Kurtosis (fat tails) and Power-Law decay.
*   **Scale Invariance:** The mechanism causing a 5% drop is structurally similar to the mechanism causing a 20% crash, just at a different scale.

### 1.2 Mathematical Framework
*   **Logarithmic Returns:** We assume continuously compounded log returns ($r_t = \ln(P_t / P_{t-1})$) are the correct unit of analysis because they are time-additive and normalize the price series for statistical operations.
*   **Lifetime Metrics:** We use lifetime Standard Deviation (Sigma) and Mean Absolute Deviation (MAD) to establish a baseline for volatility, acknowledging that these metrics are imperfect in a fat-tailed world but serve as useful descriptive statistics for "normal" variance.

### 1.3 Operational Goals
*   **Data Consistency:** The system fetches and caches data incrementally ("delta" updates) to ensure a consistent, gap-free historical record.
*   **Visual Intuitiveness:** Large deviations (outliers) must be instantly recognizable via color-coding and threshold lines.

---

## 2. Guardrails

### 2.1 Data Integrity
*   **Strict Time-Series:** The system prioritizes the integrity of the time series. New data is appended only if it chronologically follows the existing record.
*   **Data Quality Checks:**
    *   Missing data points must be filled (forward-fill) or dropped explicitly.
    *   Zeros or negative prices (in raw data) must be treated as errors.

### 2.2 Visualization
*   **Raw Data Focus:** The primary view is the raw log return series, allowing the user to see the "texture" of volatility without excessive smoothing.
*   **Thresholds:** Significant moves are contextualized against lifetime statistical properties (e.g., ±5 Sigma).

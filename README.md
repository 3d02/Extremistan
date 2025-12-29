# Project Extremistan: Operational Framework

## Project Purpose
Project Extremistan is a quantitative risk management and tactical trading framework designed to exploit the failure of Gaussian distribution models in financial markets. Conventional finance relies on the Normal Distribution, which assumes that price shocks are exponentially rare. In reality, financial time series exhibit high Kurtosis and Power-Law decay, meaning "Black Swan" events occur with significant frequency. This project utilizes 100 years of S&P 500 data to identify structural fragility, allowing a strategist to purchase Out-of-the-Money (OTM) put options when the mathematical probability of a crash is significantly higher than the price reflected in the options market.

## Mathematical Core and Reasoning

### 1. Logarithmic Returns
Instead of simple arithmetic returns, we utilize continuously compounded log returns ($r_t$):

$$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$

**Reasoning:** Arithmetic returns are not time-additive. Log returns are additive and normalize price data.

### 2. Adaptive Hill Estimator (Tail Index $\alpha$)
The central metric of the project is the Tail Index, calculated using an Adaptive Hill Estimator. It measures the decay rate of the probability density function in the left tail (losses).
We use the Danielsson–de Vries heuristic to dynamically select the optimal tail size $k$:

$$k \approx \sqrt{n}$$
$$\alpha = \left[ \frac{1}{k} \sum_{i=1}^{k} \ln\left(\frac{L_{(i)}}{L_{(k+1)}}\right) \right]^{-1}$$

**Reasoning:** Fixed thresholds fail to adapt to volatility clustering. An adaptive $k$ stabilizes the variance of the estimator.
* **$\alpha < 3.0$:** The variance of the market is theoretically unstable; large shocks are likely.
* **$\alpha \to 2.0$:** The distribution approaches infinite variance, signifying systemic fragility.

### 3. Dual-Window Alpha Comparison
The framework compares two rolling windows to determine the "momentum of fragility":
* **Climate Alpha (2-Year, Daily):** Structural baseline.
* **Weather Alpha (6-Month, Weekly):** Tactical risk, resampled to weekly frequency to reduce noise.

**Reasoning:** By comparing these two, we solve the "Ghost Effect." If the 2-year Alpha is low because of a crash 18 months ago, but the 6-month Alpha is rising, the market is "healing." Conversely, if the 6-month Alpha drops below the 2-year Alpha, fragility is accelerating.

### 4. Cross-Asset Stress
We incorporate macro signals to confirm equity fragility:
* **Term Structure Slope:** 10Y Yield - 3M Yield (`^TNX` - `^IRX`). Inversion signals recession risk.
* **Bond Volatility:** The MOVE Index (`^MOVE`). High levels (>120) indicate systemic stress.

## Strategic Logic

### Fragility Persistence (Density Rule)
A "GO" signal triggers only when the Weather Alpha (< 6M) has been structurally below the Climate Alpha (> 2Y) for a significant density (> 50%) of the recent 20-day window.

### Symmetric Healing
If the density of Weather > Climate exceeds 50%, the signal is downgraded to "WATCH," acknowledging that risk is dissipating.

### Cross-Asset Confirmation
If Fragility Density > 50% **AND** (Slope Inverted **OR** MOVE > 120), the signal upgrades to "HIGH CONVICTION."

## Dashboard Tracking and Visual Logic

### Track 1: Market Context (Price & VIX)
Plots S&P 500 (Log) vs VIX. seeks divergence (Low VIX + High Fragility).

### Track 2: Signal Engine (Climate vs. Weather)
Plots 2-year Climate Alpha (Line) and 6-month Weather Alpha (Points). "GO" depends on the density of points below the line.

### Track 3: Pain Monitor (Drawdown)
Visualizes depth and duration of market valleys.

### Track 4: Target Acquisition (Sigma Strike Zones)
Scatter plot of daily returns overlaid with fixed sigma boundaries. Targets -5$\sigma$ and -10$\sigma$ events.

## Implementation

**Executable:** `extremistan` (via CLI)

**Primary Dependencies:** `yfinance`, `pandas`, `numpy`, `matplotlib`.

## Installation and Setup

### Prerequisites
- Python 3.9 or higher.

### 1. Setup Virtual Environment
It is recommended to run this project in an isolated virtual environment (`venv`).

#### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
```

#### Windows
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 2. Install Project
Once the virtual environment is active, install the project in editable mode:

```bash
# Standard installation
pip install .

# Installation with development dependencies (for testing)
pip install .[dev]
```

## Usage

After installation, the `extremistan` command is available globally within your virtual environment.

### Online Mode (Default)
Fetches live data from Yahoo Finance.
```bash
extremistan
```

### Offline Mode
Runs the analysis using the bundled historical CSV data. Useful for backtesting or when internet access is unavailable.
```bash
extremistan --offline --csv-path data_storage/sp500_history_1927_2025.csv
```

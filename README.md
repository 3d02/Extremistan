# Market Monitor: Operational Framework

## 1. Introduction: The Philosophy of Risk
> *"Don't cross a river if it is (on average) four feet deep."* — Nassim Nicholas Taleb

Market Monitor is a quantitative tool designed to visualize financial time series and identify significant statistical outliers ("Fat Tails").

### The Problem: Mediocristan vs. Extremistan
Most financial models assume events follow a "Normal Distribution" (the Bell Curve). However, financial markets live in **"Extremistan"**, where extreme events happen far more often than predicted.

**This project helps visualize these extreme events.**

---

## 2. Core Concepts: The Math Explained

### A. Logarithmic Returns
Instead of looking at simple percentage changes, we use **Log Returns**.

$$r_t = \ln\left(\frac{P_t}{P_{t-1}}\right)$$

Log returns represent the true "distance" traveled by the price and allow us to add them up over time.

### B. Lifetime Metrics
To provide context for daily moves, we calculate metrics over the entire available history of the asset (e.g., S&P 500 since 1927).
*   **Lifetime Sigma ($\sigma$):** The standard deviation of log returns.
*   **Lifetime MAD:** The Mean Absolute Deviation.

---

## 3. Usage

### Prerequisites
- Python 3.9+

### Setup
```bash
# 1. Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

# 2. Install Dependencies
pip install .
```

### Running the Tool
```bash
# Standard Online Mode
market_monitor

# Offline Mode
market_monitor --offline --csv-path data_storage/sp500_history_1927_2025.csv
```

### Understanding the Output
The tool displays a summary of the current market state, including the latest price, drawdown, and statistical context for the day's move.

# Architecture Documentation

## 1. Overview

Project Extremistan is a quantitative analysis tool designed to detect "Black Swan" risks in financial markets using Tail Index estimation.

## 2. Current State (Monolith)

Currently, the system is implemented as a single, self-contained Python script: `extremistan.py`.

### Components (Internal to Script)
The script handles all responsibilities linearly:
1.  **Configuration:** Hardcoded constants (TICKER, WINDOWS, THRESHOLDS).
2.  **Data Ingestion:** Uses `yfinance` to download S&P 500 and VIX data.
3.  **Data Processing:**
    *   Calculates Log Returns.
    *   Computes Hill Estimator (Tail Alpha) over rolling windows.
    *   Calculates Drawdown.
4.  **Signal Logic:** Determines the regime (GO / NO-GO) based on the Alpha spread.
5.  **Visualization:** Uses `matplotlib` to render a 4-Track dashboard.

### Limitations
*   **Coupling:** Business logic is tightly coupled with plotting code.
*   **Testing:** Hard to test individual mathematical functions without running the whole script.
*   **Data Dependency:** Tightly bound to Yahoo Finance API structure.

---

## 3. Target Architecture (Modular)

As the project grows, we aim to refactor the monolith into the following independent modules:

### 3.1 Data Layer (`/data`)
*   **IngestionAdapter:** Abstract interface for data sources.
    *   `YahooFinanceAdapter`: Implementation for Yahoo.
    *   `CSVAdapter`: Implementation for local backtesting.
*   **Store:** Local caching mechanism (Parquet/HDF5) to avoid re-downloading data on every run.

### 3.2 Analytics Engine (`/analytics`)
*   **MathLib:** Pure functions for financial mathematics.
    *   `get_log_returns(series)`
    *   `hill_estimator(series, k)`
    *   `calculate_drawdown(series)`
*   This layer should have zero dependencies on plotting or external APIs.

### 3.3 Strategy Layer (`/strategy`)
*   **SignalEngine:** Accepts processed dataframes and outputs signal series.
    *   Implements the "Climate vs. Weather" logic.
    *   Configurable thresholds (e.g., Alpha < 3.0).

### 3.4 Presentation Layer (`/ui`)
*   **Dashboard:** specialized plotting module.
    *   **Track 1:** Context (Price/VIX)
    *   **Track 2:** Signal (Alphas)
    *   **Track 3:** Pain (Drawdown)
    *   **Track 4:** Target (Sigma Cones)
*   **Reporter:** Generates text-based summaries (PDF/Markdown).

## 4. Key Design Decisions

*   **Pandas as Common Tongue:** All modules exchange data via Pandas DataFrames/Series.
*   **Daily Resolution:** The core architecture is designed for Daily closing data. Intra-day data is out of scope.

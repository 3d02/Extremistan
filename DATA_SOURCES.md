# Data Sources

## 1. Primary Data Source

### Yahoo Finance (Public API)
*   **Type:** Web API / Scraper
*   **Library:** `yfinance` (Python)
*   **Coverage:** S&P 500 Index (`^GSPC`) and CBOE Volatility Index (`^VIX`).
*   **Cost:** Free
*   **Limitations:**
    *   Rate limits may apply.
    *   Data is not "tick-perfect" and may contain artifacts.
    *   Historical depth varies by ticker.

## 2. Historical Data Files

### `sp500_history_1927_2025.csv`
*   **Description:** A pre-compiled CSV file containing daily OHLCV data for the S&P 500 from 1927 to 2025.
*   **Purpose:** Used to extend the backtesting window beyond what is easily retrievable via standard free APIs, allowing analysis of the Great Depression (1929) and Black Monday (1987).
*   **Format:** Standard CSV with headers (Date, Open, High, Low, Close, Volume).

## 3. Future / Planned Sources

*   **Federal Reserve Economic Data (FRED):** For correlation with macro-economic indicators (Interest Rates, M2 Money Supply).
*   **Option Metrics:** For precise implied volatility surface data (Skew/Smile analysis), replacing the generic VIX index for strike selection.

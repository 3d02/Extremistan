# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **FRED Data Integration:** Added `FredAdapter` and `pandas-datareader` dependency to fetch official economic data from the Federal Reserve.
- **Slope Accuracy:** Switched Yield Curve Slope calculation to use `T10Y3M` (10Y-3M Constant Maturity) from FRED, replacing the Yahoo `^TNX - ^IRX` approximation.
- **Offline Data Script:** Added `scripts/fetch_offline_data.py` to generate the required CSV dataset including both Yahoo and FRED series.
- **Adaptive Fragility Refinements:**
    - **Momentum Healing:** `Alpha_6M_ROC` (>5% in 10 days) triggers early exit/downgrade to counter "Ghost Effect".
    - **Acute Stress Trigger:** `MOVE_ROC` (>10% in 5 days) triggers "High Conviction" GO signal even if levels are below absolute thresholds.
- **Strict T-1 Execution:** Live signals now explicitly reference the last available close (`iloc[-1]`) of unshifted data to align with pre-market operations.
- **ADR 0005:** Documented the shift to Daily Weather Alpha, ROC metrics, and strict T-1 handling.

### Changed
- **Weather Alpha Resolution:** Switched `Alpha_6M` calculation from Weekly (resampled) back to Daily resolution to increase sample size ($n \approx 126$) and stabilize Hill Estimator variance.
- **Backtesting Hygiene:** Applied 1-day lag (`shift(1)`) to all strategic indicators to eliminate look-ahead bias.
- **Signal Logic:** Updated `SignalEngine` to consume Cross-Asset and Healing metrics for "High Conviction" or "WATCH" states.
- **Data Ingestion:** Updated `main.py` and `DATA_SOURCES.md` to fetch and handle new tickers.
- **Specification:** Updated `SPEC.md` to reflect new mathematical and strategic assumptions.
- Updated `ARCHITECTURE.md` to reflect the modular package structure and document remaining coupling.
- Standardized ADR filenames (renamed `001` to `0002`) and format (added `Alternatives Considered`).
- Updated `CONTRIBUTING.md` to include governance sections.
- Refactored monolithic `extremistan.py` into a structured Python package.
- Moved `sp500_history_1927_2025.csv` to `data_storage/`.

### Fixed
- Enabled local test runs by adding package initializers and a pytest path shim so `extremistan` imports resolve without installation.

## [0.1.0] - 2023-10-27

### Added
- Initial release of `extremistan.py` monolith.
- Hill Estimator implementation for Tail Index Alpha.
- Dual-window (Climate vs Weather) signal logic.
- 4-Track Dashboard using Matplotlib.
- Yahoo Finance integration.

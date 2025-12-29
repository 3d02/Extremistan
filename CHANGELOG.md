# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Adaptive Hill Estimator:** Implemented Danielsson–de Vries heuristic (`k ≈ sqrt(n)`) for robust tail estimation in `math_lib.py`.
- **Cross-Asset Signals:** Integrated `^MOVE` (Bond Volatility), `^TNX` (10Y Yield), and `^IRX` (3M Yield) to detect macro stress.
- **Symmetric Healing:** Added "Healing Density" metric to downgrade signals when risk dissipates.
- **Weekly Resampling:** "Weather" Alpha (6M) is now calculated on weekly data to reduce noise and autocorrelation.
- **Regime Metrics:** Added Rolling 5Y Volatility and Z-Score calculations.
- **ADR 0004:** Documented the decision to adopt adaptive estimation and cross-asset logic.

### Changed
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

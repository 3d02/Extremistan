# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Dashboard Tracks:** Added S&P 500 (Log) + VIX overlay track and Yield Curve (10Y-3M) track to the dashboard.
- **Visual Style:** Changed log return visualization from lines to dots (semi-transparent for normal, opaque for outliers).
- **Yield Curve:** Implemented "BofA Style" yield curve plot with inversion highlighting.
- **Architecture:** Created `data.manager` and `ui.reporter` modules to separate concerns.
- **ADR 0007:** Documented dashboard restructuring.

### Changed
- **Project Rename:** Renamed project from `extremistan` to `market_monitor`.
- **Architecture:** Shifted from "Extremistan" strategy logic to a pure Market Monitor data visualization tool.
- **Data Caching:** Implemented delta-based per-ticker caching (`TICKER.parquet`) to optimize data fetching.
- **Entry Point:** Changed CLI command from `extremistan` to `market_monitor`.
- **Logging:** Replaced operational `print` statements with `logging`.

### Removed
- **Strategy Engine:** Removed `SignalEngine` and all associated trading signal logic.
- **Alpha Metrics:** Removed Hill Estimator, Weather/Climate Alpha calculations, and regime detection logic.
- **Legacy Config:** Removed deprecated references to "Extremistan" theory in documentation.

### Fixed
- **Dependencies:** Added explicit `pandas-datareader` and `requests` dependencies to fix installation issues.
- **Tests:** Fixed legacy import errors in test suite.

## [0.1.0] - 2023-10-27

### Added
- Initial release of `extremistan.py` monolith.
- Hill Estimator implementation for Tail Index Alpha.
- Dual-window (Climate vs Weather) signal logic.
- 4-Track Dashboard using Matplotlib.
- Yahoo Finance integration.

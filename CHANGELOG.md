# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Changed
- **Project Rename:** Renamed project from `extremistan` to `market_monitor`.
- **Architecture:** Shifted from "Extremistan" strategy logic to a pure Market Monitor data visualization tool.
- **Data Caching:** Implemented delta-based per-ticker caching (`TICKER.parquet`) to optimize data fetching.
- **Entry Point:** Changed CLI command from `extremistan` to `market_monitor`.

### Removed
- **Strategy Engine:** Removed `SignalEngine` and all associated trading signal logic.
- **Alpha Metrics:** Removed Hill Estimator, Weather/Climate Alpha calculations, and regime detection logic.
- **Legacy Config:** Removed deprecated references to "Extremistan" theory in documentation.

### Added
- **Lifetime Metrics:** Added calculation and display of Lifetime Standard Deviation (Sigma) and Mean Absolute Deviation (MAD).
- **Outlier Visualization:** Added color-coded outlier highlighting (±5σ, ±10σ, ±5MAD) to the main dashboard.
- **ADR 0008:** Documented the architectural shift to Market Monitor.

### Fixed
- **Dependencies:** Added explicit `pandas-datareader` and `requests` dependencies to fix installation issues.

## [0.1.0] - 2023-10-27

### Added
- Initial release of `extremistan.py` monolith.
- Hill Estimator implementation for Tail Index Alpha.
- Dual-window (Climate vs Weather) signal logic.
- 4-Track Dashboard using Matplotlib.
- Yahoo Finance integration.

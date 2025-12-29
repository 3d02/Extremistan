# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- Added CLI entry point `extremistan` in `pyproject.toml`.
- Added "Installation and Setup" section to `README.md` with detailed instructions for venv and pip install.
- Created `AGENTS.md` to define project governance and rules for AI agents.
- Enforced strict format for Architecture Decision Records (ADRs).
- Documented semantic consistency rules for file updates.
- Modular architecture implementation (`src/extremistan`).
- `Analytics` layer with pure math functions.
- `Data` layer with local Caching (Parquet) and Adapters (Yahoo, CSV).
- `Strategy` layer for signal generation.
- `UI` layer abstracting Matplotlib dashboard.
- `pytest` test suite.

### Changed
- Standardized ADR filenames (renamed `001` to `0002`) and format (added `Alternatives Considered`).
- Updated `CONTRIBUTING.md` to include governance sections.
- Refactored monolithic `extremistan.py` into a structured Python package.
- Moved `sp500_history_1927_2025.csv` to `data_storage/`.

## [0.1.0] - 2023-10-27

### Added
- Initial release of `extremistan.py` monolith.
- Hill Estimator implementation for Tail Index Alpha.
- Dual-window (Climate vs Weather) signal logic.
- 4-Track Dashboard using Matplotlib.
- Yahoo Finance integration.

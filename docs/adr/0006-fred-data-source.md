# ADR 0006: FRED Data Source Integration

## Status
Accepted

## Context
The project requires accurate Term Structure Slope calculations to assess market fragility.
Previously, the Slope was approximated using `^TNX` (10-Year Note Yield) minus `^IRX` (13-Week Bill Yield) from Yahoo Finance.
However, the user requested to use the specific `T10Y3M` series (10-Year Treasury Constant Maturity Minus 3-Month Treasury Constant Maturity) which is a standard Federal Reserve Economic Data (FRED) series.
Yahoo Finance does not consistently provide `T10Y3M`.

## Decision
We decided to integrate FRED as a secondary data source.
1.  Added `pandas-datareader` dependency to fetch data from FRED.
2.  Implemented `FredAdapter` in `src/extremistan/data/adapters.py`.
3.  Updated `main.py` to fetch `T10Y3M` from FRED and merge it with Yahoo Finance data.
4.  Updated the Slope calculation to prefer `T10Y3M` when available, falling back to the calculated spread if necessary.

## Consequences
*   **Accuracy:** Slope calculations now align with the standard Federal Reserve definition.
*   **Dependency:** Added `pandas-datareader` dependency.
*   **Data Integrity:** Requires alignment of data from two different sources (Yahoo and FRED), which is handled via index joining.
*   **Offline Mode:** Offline data CSVs must now include the `T10Y3M` column. A script `scripts/fetch_offline_data.py` was created to facilitate this.

## Alternatives Considered
*   **Manual Calculation:** Continuing to use `^TNX - ^IRX`. Rejected because the user specifically requested `T10Y3M`.
*   **Manual FRED CSV:** Downloading CSV manually. Rejected because it complicates the automated pipeline.

# ADR-0008: Project Renaming and Refactoring to Market Monitor

## Status
Accepted

## Context
The project "Extremistan" was originally designed as a specific tail-risk estimation tool based on the Hill Estimator and regime detection. The requirements have shifted towards a broader, data-centric "Market Monitor" that focuses on visualizing raw market data, identifying statistical outliers using standard deviations and MAD, and providing a clean, consistent time series via delta-based caching. The specific "Weather/Climate" alpha strategy is being deprecated in favor of raw data analysis.

## Decision
1.  **Rename**: The project is renamed from `extremistan` to `market_monitor`.
2.  **Architecture**: Shift from a Strategy/Signal-based architecture to a Data/Analysis-based architecture.
    *   Remove `SignalEngine`.
    *   Remove rolling Alpha calculations.
    *   Retain and enhance Data Ingestion (adapters, store).
    *   Retain and enhance Visualization (dashboard).
3.  **Caching**: Implement per-ticker delta caching (`TICKER.parquet`) to ensure efficient data updates without re-fetching full history.
4.  **Metrics**: Focus on Lifetime Standard Deviation (Sigma) and Mean Absolute Deviation (MAD) as the primary lenses for analyzing returns.

## Consequences
### Positive
*   **Simplicity**: The codebase is significantly simplified by removing complex strategy logic.
*   **Performance**: Delta fetching reduces bandwidth usage and processing time.
*   **Clarity**: The focus is now clearly on data presentation rather than specific theoretical interpretation.
*   **Extensibility**: Easier to add new tickers and simple metrics.

### Negative
*   **Loss of Specificity**: The unique "Tail Index" insight is removed (though can be re-added as a metric later if needed).
*   **Migration**: Existing users (if any) must migrate to the new command `market_monitor` and potentially clear old cache.

## Alternatives Considered
*   **Keep Name, Change Logic**: Rejected because the name "Extremistan" implies a specific theoretical framework that is being deemphasized.
*   **Create New Repo**: Rejected to maintain the git history and infrastructure of the current setup.

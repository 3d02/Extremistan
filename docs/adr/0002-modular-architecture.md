# ADR 0002: Modular Architecture Refactor

## Status
Accepted

## Context
The project started as a single script `extremistan.py` to prove the concept of Hill Estimator-based tail risk detection. As we move towards a production-grade system and potential web deployment, the monolithic structure poses several challenges:
- **Coupling:** Business logic is intertwined with plotting code.
- **Testability:** It is difficult to unit test mathematical functions in isolation.
- **Extensibility:** Adding new data sources or changing the visualization engine is risky.

## Decision
We will refactor the application into a modular Python package `src/extremistan` with the following components:

1.  **Analytics Layer (`analytics`):** Pure functions for financial mathematics (Log returns, Hill Alpha, Drawdown).
2.  **Data Layer (`data`):** Abstract `DataSource` interface with specific adapters (`YahooFinanceAdapter`, `CSVAdapter`).
    *   **Caching:** We will implement a local caching mechanism using Parquet files in a `.cache` directory to reduce external API calls and speed up development.
3.  **Strategy Layer (`strategy`):** Encapsulates the signal generation logic (Climate vs Weather comparison).
4.  **Presentation Layer (`ui`):** Abstracts the visualization logic. Initially implements a `MatplotlibDashboard`.

## Consequences
### Positive
- **Testability:** Each module can be tested independently.
- **Maintainability:** Clear separation of concerns makes the code easier to understand and modify.
- **Flexibility:** The UI can be swapped for a web framework (e.g., Streamlit/Dash) without touching the core logic. Data sources can be added easily.

### Negative
- **Complexity:** Increased number of files and boilerplate code compared to a single script.
- **Setup:** Requires a proper Python package structure and installation (handled via `pyproject.toml`).

## Alternatives Considered
*   **Maintaining the Monolith:** We considered keeping the single `extremistan.py` script for simplicity. However, this was rejected as it makes testing difficult, hinders collaboration, and makes future web integration much harder due to tight coupling between logic and plotting.

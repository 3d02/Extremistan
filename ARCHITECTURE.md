# Architecture Documentation

## 1. Overview

Project Extremistan is a quantitative analysis tool designed to detect "Black Swan" risks in financial markets using Tail Index estimation.

## 2. Current State (Modular Package)

The system is implemented as a structured Python package under `src/extremistan/`.

### 2.1 Package Structure

*   **`data/` (Data Layer)**
    *   `adapters.py`: Contains `YahooFinanceAdapter` and `CSVAdapter`. Both return Pandas DataFrames.
    *   `store.py`: Handles local caching using Parquet files.
    *   `interfaces.py`: Defines the `DataSource` protocol.

*   **`analytics/` (Analytics Engine)**
    *   `math_lib.py`: Pure functions for financial mathematics (Log Returns, Adaptive Hill Estimator, Rolling Volatility, Z-Scores, Rate of Change).

*   **`strategy/` (Strategy Layer)**
    *   `signal_engine.py`: Contains `SignalEngine` class. Evaluates "Climate vs. Weather" logic with Cross-Asset Confirmation (Level + Acute ROC) and Momentum Healing returns a `SignalResult`.

*   **`ui/` (Presentation Layer)**
    *   `dashboard.py`: Contains `MatplotlibDashboard`. Renders the 4-Track visualization.

*   **`main.py` (Orchestration)**
    *   The entry point of the application. Handles configuration, data normalization, weekly resampling, signal synchronization (lagging), and orchestrates the flow.

### 2.2 Component Interaction

The following diagram illustrates the data flow managed by `main.py`:

```mermaid
sequenceDiagram
    participant Main as main.py
    participant Data as Data Layer (Adapters)
    participant Analytics as Analytics Layer
    participant Strategy as Strategy Layer
    participant UI as UI Layer

    Note over Main: 1. Configuration & Setup
    Main->>Data: get_data(SPX, VIX, MOVE, TNX, IRX)
    Data-->>Main: Raw DataFrame

    Note over Main: 2. Normalization & Pre-Processing
    Main->>Main: Standardize Ticker Columns

    Note over Main: 3. Analytics Processing
    Main->>Analytics: get_log_returns(SPX)
    Main->>Analytics: get_hill_alpha(LogReturns, adaptive=True)
    Main->>Analytics: get_rate_of_change(Alpha, MOVE)
    Main->>Analytics: get_rolling_volatility(LogReturns)
    Main->>Analytics: calculate_drawdown(SPX)
    Analytics-->>Main: Updated DataFrame (Alphas, ROCs, Drawdown, RegimeMetrics)

    Note over Main: 4. Backtesting Hygiene
    Main->>Main: Shift(1) all indicators (Alphas, Slope, MOVE, ROCs)

    Note over Main: 5. Signal Evaluation
    Main->>Strategy: evaluate(Shifted_Alphas, Densities, CrossAsset, ROCs)
    Strategy-->>Main: SignalResult (GO/NO-GO)

    Note over Main: 6. Reporting & Visualization
    Main->>Main: Print Text Report
    Main->>UI: render(DataFrame, Context)
```

### 2.3 Remaining Monolithic Coupling

While the code is physically modular, `main.py` retains significant logic that belongs in specific layers:

1.  **Normalization & Resampling:** `main.py` manually maps columns and handles the resampling for weekly alpha. This logic is complex and could be encapsulated.
2.  **Orchestration Overload:** The script linearizes the entire process. There is no `Application` class wrapping the lifecycle.
3.  **Reporting:** Text-based output is printed directly to `stdout` within `main.py`.

---

## 3. Next Steps (Target Architecture)

To further decouple the system, the following refactoring steps are proposed:

1.  **Move Normalization:** Push the column mapping and cleaning logic into a `DataTransformer` or within specific `Adapters` in the Data Layer. The Data Layer should return a standardized schema (guaranteed `SPX`, `VIX` columns).
2.  **Dedicated Orchestrator:** Create an `Engine` or `App` class in a new core module to encapsulate the execution flow, making `main.py` a thin CLI wrapper.
3.  **Decouple Reporting:** Create a `TextReporter` in the UI layer to handle the "Operational Briefing" output, separating presentation from logic.

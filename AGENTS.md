# Agent Rules and Governance

This file outlines the strict rules and governance standards for the Extremistan project. All AI agents and contributors must adhere to these guidelines.

## 1. Architecture Decision Records (ADRs)

We use ADRs to capture significant architectural decisions.

### Format Rules
*   **Numbering:** Must use a 4-digit sequence (e.g., `0001`, `0002`).
*   **Filename:** `XXXX-title-slug.md` (e.g., `0001-use-hill-estimator.md`).
*   **Mandatory Sections:**
    1.  **Status**: Must be one of `Proposed`, `Accepted`, `Rejected`, `Deprecated`, `Superseded`.
    2.  **Context**: The problem description and motivation.
    3.  **Decision**: The solution adopted.
    4.  **Consequences**: The results (both Positive and Negative).
    5.  **Alternatives Considered**: Other options that were evaluated.

### Example Template
```markdown
# ADR-XXXX: Title

## Status
Accepted

## Context
...

## Decision
...

## Consequences
### Positive
* ...
### Negative
* ...

## Alternatives Considered
* ...
```

## 2. Changelog

We follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standard.

### Rules
*   **Append-Only:** Never rewrite history.
*   **Unreleased:** Add new changes to the `[Unreleased]` section at the top.
*   **Categories:** Group changes by type:
    *   `Added` for new features.
    *   `Changed` for changes in existing functionality.
    *   `Deprecated` for soon-to-be removed features.
    *   `Removed` for now removed features.
    *   `Fixed` for any bug fixes.
    *   `Security` in case of vulnerabilities.

## 3. Semantic Consistency

When code changes are made, all semantically related documentation must be updated to maintain consistency.

### Checklist
Before submitting changes, verify the following have been updated if affected:
- [ ] **Docs**: API documentation, docstrings.
- [ ] **Architecture**: ADRs (if a decision changed) or `ARCHITECTURE.md`.
- [ ] **Changelog**: Add an entry for the change.
- [ ] **README**: Update installation or usage instructions.

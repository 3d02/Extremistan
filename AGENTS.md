# Agent Rules and Governance

This file outlines the strict rules and governance standards for the Market Monitor project. All AI agents and contributors must adhere to these guidelines.

## General Principles
- Adhere to the Zen of Python (`import this`): Prioritize readability, simplicity, and explicitness.
- Write clean, idiomatic Python code suitable for latest version.
- Use type hints extensively for all functions, methods, variables, and return values.
- Prefer descriptive, meaningful names for variables, functions, and classes (snake_case for variables/functions, CamelCase for classes).
- Avoid premature optimization; favor clarity unless performance is critical.

## Code Style and Formatting
- Follow PEP 8 strictly: Limit lines to 88 characters (Black formatter default), use 4-space indentation, and surround top-level functions/classes with two blank lines.
- Use Black for formatting, Ruff or flake8 for linting, and mypy for type checking.
- Always format code with Black and ensure it passes linting/type checking before finalizing changes.
- Use single quotes for strings unless double quotes are needed for interpolation.
- Prefer f-strings for string formatting over `.format()` or `%`.

## Imports
- Organize imports in this order: standard library, third-party, local/project modules.
- Use absolute imports over relative imports.
- Avoid wildcard imports (`*`); import specific names.
- Group imports with blank lines as per PEP 8.

## Functions and Classes
- Use type annotations (`from typing import ...`) for all parameters and returns.
- Write concise docstrings in Google or NumPy style, including Args, Returns, and Raises sections.
- Prefer functions over classes unless state or inheritance is required.
- Use dataclasses or Pydantic models for data structures.
- Avoid global variables; use dependency injection or configuration where needed.

## Error Handling and Logging
- Use structured exceptions; raise specific errors rather than generic `Exception`.
- Prefer context managers (`with` statements) for resource management.
- Use the `logging` module instead of `print()` for debugging or informational messages.
- Log at appropriate levels (DEBUG, INFO, WARNING, ERROR).

## Testing
- Write tests using `pytest`.
- Use descriptive test function names starting with `test_`.
- Prefer `pytest` fixtures over setup/teardown methods.
- Use plain `assert` statements; avoid `self.assert*` patterns.
- Aim for high coverage: Include unit tests for all new/changed functions.
- Run tests with `pytest` and ensure they pass before completing tasks.

## Dependencies and Environment
- Use `uv` or `poetry` for dependency management if configured; otherwise, prefer `pip` with `requirements.txt`.
- Pin dependencies appropriately in `pyproject.toml` or `requirements.txt`.
- Create virtual environments with `venv` or `uv venv`.

## Security and Best Practices
- Validate all external inputs (use Pydantic if applicable).
- Avoid hardcoded secrets; use environment variables or secrets management.
- Sanitize user inputs to prevent injection attacks.
- Follow the principle of least privilege for any external API calls.

## Workflow Instructions
- After code changes, always run formatters, linters, type checkers, and tests.
- If tests fail, fix them iteratively.
- Provide clear reasoning in plans before implementing changes.
- Update documentation (e.g., README.md or docstrings) as needed.

## Architecture Decision Records (ADRs)

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

## Changelog

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

## Semantic Consistency

When code changes are made, all semantically related documentation must be updated to maintain consistency.

### Checklist
Before submitting changes, verify the following have been updated if affected:
- [ ] **Docs**: API documentation, docstrings.
- [ ] **Architecture**: ADRs (if a decision changed) or `ARCHITECTURE.md`.
- [ ] **Changelog**: Add an entry for the change.
- [ ] **README**: Update installation or usage instructions.

Adhere to these rules in all interactions with this project to ensure consistency and quality.

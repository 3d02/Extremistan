# Contributing to Project Extremistan

We welcome contributions to Project Extremistan! Whether you are a human developer or an AI agent, please follow these guidelines to ensure the project remains robust and scientifically rigorous.

## 1. General Workflow

1.  **Fork & Clone:** Fork the repository and clone it locally.
2.  **Branch:** Create a new branch for your feature or bugfix (`git checkout -b feature/my-new-feature`).
3.  **Code:** Implement your changes.
4.  **Test:** Run the script locally to ensure no regressions.
5.  **Commit:** Use clear, descriptive commit messages.
6.  **Pull Request:** Submit a PR to the main branch.

## 2. Guidelines for Human Contributors

*   **Issue Tracking:** Please check existing issues before starting work. If you find a bug, open a new issue.
*   **Documentation:** If you change the logic (e.g., the Hill Estimator formula), you **must** update the `SPEC.md` and `README.md` to reflect the new assumptions.
*   **Code Style:** Follow standard Python PEP 8 guidelines. Keep functions small and focused.

## 3. Guidelines for AI Contributors (Agents)

AI agents interacting with this codebase must adhere to strict verification protocols:

*   **Self-Correction:** If you encounter an error, do not blindly retry. Analyze the error message, hypothesis the cause, and fix the root problem.
*   **Verification:** You **must** verify your changes.
    *   If you create a file, check that it exists.
    *   If you modify code, run it to ensure it executes without crashing.
*   **Test Cases:** When fixing a bug, first create a reproduction case (if possible), then fix it, then verify the fix.
*   **Documentation Alignment:** AI agents must check `SPEC.md` and `ARCHITECTURE.md` to ensure their code changes do not violate the core architectural or mathematical principles.
*   **Tagging:** Please tag your PRs with `[AI-Generated]` if the code was primarily written by an LLM.

## 4. Governance

### Architecture Decision Records (ADRs)
We use ADRs to capture significant architectural decisions. If your change involves a major design decision (e.g., adding a new database, changing the math library, restructuring modules), you must create a new ADR.

*   **Location:** `docs/adr/`
*   **Naming:** `XXXX-title-slug.md` (e.g., `0003-add-database.md`).
*   **Format:** Follow the strict template defined in `AGENTS.md`.

### Changelog
We follow the [Keep a Changelog](https://keepachangelog.com/en/1.0.0/) standard.

*   **File:** `CHANGELOG.md`
*   **Rules:**
    *   Add your changes to the `[Unreleased]` section at the top of the file.
    *   Categorize them correctly (`Added`, `Changed`, `Fixed`, etc.).
    *   Never rewrite past release notes.

## 5. Testing

Currently, the project is a single script. To test:

```bash
python extremistan.py
```

Ensure the script runs to completion and displays the dashboard (or prints the textual output if in a headless environment). Future versions will include a dedicated test suite.

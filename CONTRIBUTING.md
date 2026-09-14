# Contributing to News Tracker (Engineering Standards)

This project strictly follows the **Engineering Standards Manual** to ensure production stability, non-regression, and high code quality.

## 1. Git Architecture (Branching Strategy)
- **`main` is protected:** No direct pushes are allowed (except for the automated bot updating the reports). All code changes must go through a Pull Request (PR).
- **`develop` branch:** Use this branch to aggregate feature work.
- **`feature/<name>`:** Branch off `develop` for new features.
- **`hotfix/<name>`:** Branch off `main` for critical production fixes.

## 2. Commit Standards (Conventional Commits)
Commits must be machine-readable and follow the Conventional Commits format:
`<type>[optional scope]: <description>`

**Valid Types:**
- `feat:` New feature
- `fix:` Bug fix
- `refactor:` Code change that neither fixes a bug nor adds a feature
- `test:` Adding or updating tests
- `ci:` Changes to CI configuration files
- `docs:` Documentation changes

## 3. CI/CD Pipeline
All Pull Requests trigger an automated CI pipeline (`ci.yml`) which runs three mandatory checks:
1. **Linting:** Validates PEP8 style using `flake8`.
2. **Security Scan:** Analyzes code for vulnerabilities using `bandit` (Note: `B501` is ignored by design due to corporate Zscaler constraints).
3. **Tests:** Runs the `pytest` suite.

**The PR cannot be merged if any of these checks fail.**

## 4. Software Quality & Tests
Untested code is considered broken code.
- **Minimum Coverage:** The project enforces a strict **80% minimum code coverage**. The CI pipeline will automatically fail if the coverage drops below this threshold.
- **Isolation:** Tests must be deterministic and must not make actual network requests (e.g., Gemini API, RSS HTTP calls). All external dependencies must be mocked using `unittest.mock` or `pytest-mock`.
- **Test Execution:** Run tests locally before opening a PR:
  ```bash
  pytest tests/ -v --cov=news_tracker --cov-fail-under=80
  ```

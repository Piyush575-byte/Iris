# Contributing to Iris

Thank you for your interest in contributing to Iris! Every contribution matters — whether it's fixing a bug, adding a feature, improving docs, or just reporting an issue.

## Getting Started

1. **Fork** the repository on GitHub
2. **Clone** your fork locally:
   ```bash
   git clone https://github.com/<your-username>/Iris.git
   cd Iris
   ```
3. **Create a branch** for your work:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Setup

Iris is designed to have **zero external dependencies** on Linux/macOS. On Windows, the only dependency is `pywinpty`:

```bash
# Windows only
pip install -r requirements.txt
```

Run the CLI to verify your setup:
```bash
python iris.py --help
```

## Making Changes

- Keep changes **focused** — one feature or fix per PR
- Follow existing **code style** (PEP 8)
- Add docstrings for new functions
- Test on your platform before submitting

## Submitting a Pull Request

1. Commit your changes with a clear, descriptive message:
   ```bash
   git commit -m "Add: brief description of what you did"
   ```
2. Push to your fork:
   ```bash
   git push origin feature/your-feature-name
   ```
3. Open a **Pull Request** against the `main` branch
4. Fill out the PR template and describe your changes

## Reporting Bugs

- Use the [Bug Report](https://github.com/piyush1910dtu-dot/Iris/issues/new?template=bug_report.md) issue template
- Include your OS, Python version, and steps to reproduce

## Suggesting Features

- Use the [Feature Request](https://github.com/piyush1910dtu-dot/Iris/issues/new?template=feature_request.md) issue template
- Explain the problem you're solving and your proposed approach

## Code of Conduct

This project follows the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md). By participating, you agree to uphold this code.

---

Thank you for helping make Iris better! 🎉

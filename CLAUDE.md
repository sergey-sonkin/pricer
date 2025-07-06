See @README.md for project overview
See @TODO.md to view dev blog and current goals
See @tests/test-cases.md for test cases to compare against when making changes (if relevant). Please seek to update this with new features

# Code Quality Standards

When writing or modifying code, please ensure it follows our quality standards:

## Before committing code:
- Run `ruff check --fix .` to automatically fix linting issues
- Run `ruff format .` to format code consistently
- Or simply commit - pre-commit hooks will handle this automatically

## For manual checks:
- `ruff check .` - Check for linting violations
- `ruff format --diff .` - Preview formatting changes
- `uv run pre-commit run --all-files` - Run all quality checks

All code should pass ruff checks without violations. Pre-commit hooks will automatically format and check code on every commit.

# Dependency Management Standards

When writing code that uses external dependencies:

## Import Standards:
- **NO try/except blocks around imports** - dependencies should be properly declared and available
- Use direct imports: `from package import module`
- If a dependency is missing, the code should fail fast with a clear error message

## Environment Variables:
- All scripts and library code should load `.env` files using `python-dotenv`
- Add `from dotenv import load_dotenv` and call `load_dotenv()` at module level
- Environment variables should be documented in `.env.example`

## Dependency Declaration:
- Add all dependencies to `pyproject.toml` using `uv add package_name`
- Never assume dependencies are available without declaring them

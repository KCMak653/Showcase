# TO DO

## Python project layout & imports (revisit)

The app currently mixes import styles (flat `from constants import …` vs package paths like `from showcase.llm_io.providers import …`), which only works when run from `showcase/` with `python3 main.py`. Running `python -m showcase.main` from the repo root fails.

**Goal:** Make imports and execution robust and consistent (industry-standard layout).

- [x] Add `pyproject.toml` at repo root (`Showcase/`) with package metadata and dependencies
- [x] Use a single top-level package: `showcase` (optional: move to `src/showcase/` layout)
- [x] Replace flat imports with absolute package imports (e.g. `from showcase.constants import …`, `from showcase.llm_io.providers import OpenAIModelIO`)
- [x] Use relative imports only *within* the same package where appropriate (e.g. `from .exceptions import RateLimitedException`)
- [x] Install in editable mode: `pip install -e .` from repo root
- [x] Define a CLI entry point in `pyproject.toml` (e.g. `showcase = "showcase.main:handle"`) so the app runs from any cwd
- [x] Document run instructions in README: venv, `pip install -e .`, `showcase` or `python -m showcase.main`
- [x] Avoid `sys.path` hacks and cwd-dependent `python main.py` as the only supported path

**References:** PEP 517/518 (`pyproject.toml`), hatchling/setuptools, editable installs.

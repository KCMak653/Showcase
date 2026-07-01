# TO DO

## Python project layout & imports (revisit)

The app currently mixes import styles (flat `from constants import …` vs package paths like `from llm_io.providers import …`), which only works when run from `spotify_local_shows/` with `python3 main.py`. Running `python3 -m spotify_local_shows.main` from the repo root fails.

**Goal:** Make imports and execution robust and consistent (industry-standard layout).

- [ ] Add `pyproject.toml` at repo root (`Showcase/`) with package metadata and dependencies
- [ ] Use a single top-level package: `spotify_local_shows` (optional: move to `src/spotify_local_shows/` layout)
- [ ] Replace flat imports with absolute package imports (e.g. `from spotify_local_shows.constants import …`, `from spotify_local_shows.llm_io.providers import OpenAIModelIO`)
- [ ] Use relative imports only *within* the same package where appropriate (e.g. `from .exceptions import RateLimitedException`)
- [ ] Install in editable mode: `pip install -e .` from repo root
- [ ] Define a CLI entry point in `pyproject.toml` (e.g. `showcase = "spotify_local_shows.main:handle"`) so the app runs from any cwd
- [ ] Document run instructions in README: venv, `pip install -e .`, `showcase` or `python -m spotify_local_shows.main`
- [ ] Avoid `sys.path` hacks and cwd-dependent `python main.py` as the only supported path

**References:** PEP 517/518 (`pyproject.toml`), hatchling/setuptools, editable installs.

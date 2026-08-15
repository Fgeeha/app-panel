# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Single-file Flask app (`app.py`, ~130 lines) serving one page: a list of links to
local network services, read from `apps.yaml`. No database, no build step, no
framework beyond Flask + PyYAML.

## Commands

```bash
# Setup
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp apps.yaml.example apps.yaml          # apps.yaml is gitignored

# Dev server (Flask built-in, port 8082)
.venv/bin/python app.py

# Production (what the systemd unit runs)
.venv/bin/gunicorn --workers 2 --timeout 30 --bind 0.0.0.0:8082 app:app

# Tests — the whole suite, there is no runner and no pytest dependency
.venv/bin/python test_app.py            # prints OK on success
```

## Architecture notes

**Config is read per request, not at import.** `load_apps()` is called inside each
route handler, so editing `apps.yaml` takes effect without a restart. Keep it that
way — don't cache the parsed config at module level.

**`load_apps()` never raises.** Missing file, broken YAML, non-list root, and
entries without `name`/`url` all degrade to an empty or filtered list plus a log
line. The page renders empty rather than returning 500. New config-handling code
must preserve this: `/healthz` returns `degraded` (not an error) on an empty list,
and the systemd unit's `ExecStartPost` readiness probe polls `/healthz` expecting
HTTP 200 regardless of `status`.

**Config path is a module global.** `CONFIG_PATH` is read from the environment at
import time; `test_app.py` swaps it by assigning `app_module.CONFIG_PATH` between
assertions. Any refactor that reads the env var inside `load_apps()` instead will
silently break the tests.

**HTML lives in `HTML_TEMPLATE`, a string in `app.py`** rendered via
`render_template_string` — there is no `templates/` directory. Styling is inline
CSS with a `prefers-color-scheme` dark variant.

## Conventions

- Docs (`README.md`, `TODO.md`), commit messages, and user-facing UI text are in
  Russian; code, identifiers, and code comments are in English.
- `TODO.md` holds the reasoned backlog — mainly the authentication story. The panel
  is intentionally unauthenticated and assumes a trusted LAN; read `TODO.md` before
  proposing auth, TLS, or systemd hardening changes, as the options are already
  weighed there.
- Changes to routes or config parsing should come with an assertion in
  `test_app.py`; it is the only safety net.

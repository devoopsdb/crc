# CRC Full-Stack Modernization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Modernize the CRC cable-reel calculator on Django 6.1 — fix all critical formula/backend bugs, normalize the data model, add 4-language i18n, and rebuild the frontend with a custom Bootstrap 5.3 design system (light/dark themes, best-practice UI/UX).

**Architecture:** Server-rendered Django 6.1 templates + SQLite. Pure calculation logic extracted to `app/calc.py` (tested independently). Data normalized into `CableCal` (header) + `CableLineItem` (rows) + `CalculationSettings` (singleton). i18n via path-based `i18n_patterns` (en/az/ru/tr). Frontend: local Bootstrap 5.3.3 + custom `app.css` token layer + vanilla JS (no jQuery), Bootstrap 5.3 color modes for theming.

**Tech Stack:** Python 3.13, Django 6.1, SQLite, Bootstrap 5.3.3 (local), Bootstrap Icons (local), vanilla JS, Django test runner.

**Spec:** `docs/superpowers/specs/2026-08-23-crc-fullstack-modernization-design.md`

## Global Constraints

- **Python ≥ 3.13**, **Django == 6.1** (per `uv.lock`); `requirements.txt` must match `uv.lock` exactly: `Django==6.1`, `asgiref==3.12.1`, `sqlparse==0.6.0` (+ `tzdata` on Windows).
- **No new runtime dependencies** (no django-environ, no django-rosetta, no pytest, no jQuery, no npm build). Bootstrap + Bootstrap Icons vendored locally under `crc/static/`.
- **No `.env` file.** Use stdlib `os.environ.get()` with safe defaults only.
- **No authentication.** All views remain public.
- **i18n languages:** `en`, `az`, `ru`, `tr` — all LTR.
- **Migrations MUST be committed to git** (the `.gitignore` rule that ignored them is removed in Task 0.2).
- **Existing data must survive:** 3 `CableCal`, 11 `ReelsList`, 3 `TransportList` records are migrated, never destroyed.
- **No inline `style="..."`** in any template after Phase 4.
- **No `<h7>`** or other invalid HTML elements.
- Commit after every task (or logical step group). Run `python manage.py test` before each commit in Phases 1–3 and 5.
- Strings: model `verbose_name`/`help_text`, form labels, and all template UI text use `gettext_lazy` / `{% trans %}` / `{% blocktrans %}` from Phase 3 onward. Phase 1–2 may use English literals first; Phase 3 marks them.

---

## File Structure (target state)

```
crc/
├─ .gitignore                      (modify — Task 0.2)
├─ requirements.txt                (modify — Task 0.1)
├─ README.md                       (rewrite — Task 0.6)
├─ pyproject.toml                  (unchanged)
├─ manage.py                       (unchanged)
├─ crc/
│  ├─ settings.py                  (modify — Tasks 0.4, 3.1)
│  ├─ urls.py                      (modify — Task 3.2)
│  ├─ wsgi.py, asgi.py             (unchanged)
│  └─ static/
│     ├─ bootstrap/{css,js}/       (keep — local BS 5.3.3)
│     ├─ icons/                    (NEW — Bootstrap Icons, Task 4.2)
│     ├─ css/app.css               (NEW — design system, Task 4.3)
│     ├─ js/app.js                 (NEW — theme/lang/formset, Task 4.4)
│     └─ img/{crc-logo.svg, ... favicon.svg}  (keep + add favicon, Task 4.2)
├─ app/
│  ├─ calc.py                      (NEW — pure formula, Task 1.1)
│  ├─ models.py                    (modify — Tasks 2.1, 2.2)
│  ├─ forms.py                     (modify — Task 2.3)
│  ├─ views.py                     (modify — Tasks 1.3, 2.4, 3.3)
│  ├─ urls.py                      (modify — Tasks 1.4, 3.2)
│  ├─ admin.py                     (modify — Task 5.1)
│  ├─ apps.py                      (unchanged)
│  ├─ migrations/
│  │  ├─ 0001..0003                (commit existing — Task 0.2)
│  │  ├─ 0004_calcsettings_lineitem.py        (NEW — Task 2.2)
│  │  └─ 0005_split_cablecal_to_lineitems.py  (NEW — Task 2.5)
│  ├─ tests/
│  │  ├─ __init__.py
│  │  ├─ test_calc.py              (NEW — Task 1.2)
│  │  ├─ test_models.py            (NEW — Task 2.6)
│  │  ├─ test_views.py             (NEW — Task 2.7)
│  │  └─ test_i18n.py              (NEW — Task 3.6)
│  └─ templates/app/
│     ├─ base.html                 -> moved to templates/base.html (Task 4.5)
│     ├─ cable_cal.html            (rewrite — Task 4.6)
│     ├─ cable_cal_list.html       (rewrite — Task 4.7)
│     ├─ cable_cal_detail.html     (rewrite — Task 4.8)
│     ├─ cable_cal_confirm_delete.html (rename from cable_cal_del.html — Task 4.9)
│     ├─ reels.html, reels_detail.html, reels_add.html, reels_confirm_delete.html (Tasks 4.10–4.11)
│     ├─ transport.html, transport_detail.html, transport_add.html, transport_confirm_delete.html (Tasks 4.10–4.11)
│     └─ partials/_navbar.html, _sidebar.html, _footer.html, _theme_init.html, _lang_switcher.html (Task 4.5)
├─ templates/base.html             (rewrite — Task 4.5)
├─ locale/{en,az,ru,tr}/LC_MESSAGES/django.{po,mo}  (NEW — Task 3.5)
└─ docs/superpowers/{specs,plans}/  (this work)
```

**Deleted:** `main.py`, `static/` (duplicate collectstatic tree), `crc/static/css/style.css`, `crc/static/css/vendor.bundle.base.css`, `crc/static/css/themify-icons.css`, `crc/static/fonts/themify.*`, `crc/static/js/vendor.bundle.base.js`, `crc/static/js/dashboard.js`, `crc/static/js/chart.js`, `crc/static/js/documentation.js`, `crc/static/js/file-upload.js`, `crc/static/js/tabs.js`, `crc/static/js/tooltips.js`, `crc/static/js/jquery.cookie.js`, `crc/static/js/off-canvas.js`, `crc/static/js/hoverable-collapse.js`, `crc/static/js/template.js`, `crc/static/js/todolist.js`, `app/templates/app/cal_cable.html`, `app/templates/app/tessst.html`.

---

## Phase 0 — Foundation & Infrastructure

### Task 0.1: Sync dependency manifests

**Files:**

- Modify: `requirements.txt`

**Interfaces:** Produces a `requirements.txt` matching `uv.lock` so `pip install -r requirements.txt` installs Django 6.1.

- [ ] **Step 1: Rewrite `requirements.txt`** to match `uv.lock`:

```text
Django==6.1
asgiref==3.12.1
sqlparse==0.6.0
tzdata ; sys_platform == "win32"
```

- [ ] **Step 2: Verify install is consistent**

Run: `uv run python -c "import django; assert django.get_version()=='6.1'"`
Expected: no output, exit 0.

- [ ] **Step 3: Commit**

```bash
git add requirements.txt
git commit -m "chore: sync requirements.txt to uv.lock (Django 6.1)"
```

### Task 0.2: Fix `.gitignore` and commit migrations; remove duplicate `static/`

**Files:**

- Modify: `.gitignore`
- Delete: `static/` (entire duplicate collectstatic tree)
- Track: `app/migrations/0001_initial.py`, `app/migrations/0002_*.py`, `app/migrations/0003_*.py`

**Interfaces:** Produces a repo where `git clone && uv sync && uv run python manage.py migrate` works with no `makemigrations` needed.

- [ ] **Step 1: Edit `.gitignore`** — remove the migrations-ignore block and add STATIC_ROOT ignore. Replace:

```text
# Migrations
**/migrations/*.py
!**/migrations/__init__.py
```

with:

```text
# Django
*.mo
# Migrations are committed (do NOT ignore them)
# Collectstatic output (STATIC_ROOT) is generated, not committed:
/static/
```

(Keep the existing `db.sqlite3`, `.venv/`, `__pycache__/`, `*.pyc`, `.env`, `.idea/`, `.vscode/` rules. Ensure `*.pot` is NOT ignored — remove any `*.pot` line so the translation template can be committed if desired; `.po` files are committed, `.mo` ignored.)

- [ ] **Step 2: Force-add the existing migrations** (they were previously ignored):

```bash
git add -f app/migrations/0001_initial.py app/migrations/0002_cablecal_bending_radius_cablecal_brutto_1_and_more.py app/migrations/0003_cablecal_reel_name.py
git add app/migrations/__init__.py
```

- [ ] **Step 3: Remove the duplicate committed `static/` tree** (sources live in `crc/static/`):

```bash
git rm -r --cached static/
rm -rf static/
```

- [ ] **Step 4: Verify**

Run: `git status --short` → migrations staged, `static/` gone.
Run: `uv run python manage.py check` → no errors.

- [ ] **Step 5: Commit**

```bash
git add .gitignore app/migrations/
git commit -m "fix: stop ignoring migrations; ignore collectstatic output; drop duplicate static/ tree"
```

### Task 0.3: Remove dead code & debug leftovers

**Files:**

- Delete: `main.py`
- Delete: `app/templates/app/cal_cable.html`, `app/templates/app/tessst.html`
- Modify: `app/views.py` (remove `x` view)
- Modify: `app/urls.py` (remove `path("x/", x)`)

**Interfaces:** Produces a clean `app/views.py` with no `x` function; no dead templates.

- [ ] **Step 1: Delete dead files**

```bash
rm main.py app/templates/app/cal_cable.html app/templates/app/tessst.html
```

- [ ] **Step 2: Remove the `x` view** from `app/views.py` — delete:

```python
def x(request):
    return render(request, "app/tessst.html")
```

- [ ] **Step 3: Remove the `x` route** from `app/urls.py` — delete the line `path("x/", x),`.

- [ ] **Step 4: Verify**

Run: `uv run python manage.py check`
Expected: no errors.

- [ ] **Step 5: Commit**

```bash
git add app/views.py app/urls.py
git commit -m "chore: remove dead code (main.py, cal_cable/tessst templates, x view/route)"
```

### Task 0.4: Modernize `settings.py` (env vars, STORAGES, doc comments, favicon-ready)

**Files:**

- Modify: `crc/settings.py`

**Interfaces:** Produces env-driven settings with safe defaults; `STORAGES` dict; doc comments referencing 6.1.

- [ ] **Step 1: Replace top of `settings.py`** — update the doc comment and the security block. Replace:

```python
"""
Django settings for crc project.

Generated by 'django-admin startproject' using Django 5.0.6.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "django-insecure--1gl9g+%(*m%sk!*g6+fc^1i+5t@f45e1tqc0liwb$kn#@wzyd"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["127.0.0.1", "10.1.65.92", "*"]
```

with:

```python
"""
Django settings for crc project.

For more information on this file, see
https://docs.djangoproject.com/en/6.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/6.1/ref/settings/
"""

import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


def _env_bool(name, default):
    return os.environ.get(name, str(default)).lower() in {"1", "true", "yes", "on"}


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/6.1/howto/deployment/checklist/

SECRET_KEY = os.environ.get(
    "DJANGO_SECRET_KEY",
    "django-insecure--1gl9g+%(*m%sk!*g6+fc^1i+5t@f45e1tqc0liwb$kn#@wzyd",
)

DEBUG = _env_bool("DJANGO_DEBUG", True)

ALLOWED_HOSTS = os.environ.get(
    "DJANGO_ALLOWED_HOSTS", "127.0.0.1,localhost,10.1.65.92"
).split(",")

CSRF_TRUSTED_ORIGINS = [
    o for o in os.environ.get(
        "DJANGO_CSRF_TRUSTED_ORIGINS", "http://127.0.0.1,http://localhost"
    ).split(",") if o
]
```

- [ ] **Step 2: Modernize static/media to `STORAGES` dict.** Replace:

```python
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = os.path.join(BASE_DIR, "static")
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "crc/static"),
]
```

with:

```python
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/6.1/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "static"
STATICFILES_DIRS = [BASE_DIR / "crc" / "static"]

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}
```

- [ ] **Step 3: Update remaining doc-comment version strings** `en/5.0/` → `en/6.1/` (Database, Password validation, Internationalization, Static files, Default auto_field sections). Leave `LANGUAGE_CODE`, `USE_I18N`, `USE_TZ`, `DATETIME_FORMAT` as-is for now (i18n is wired in Task 3.1).

- [ ] **Step 4: Verify**

Run: `uv run python manage.py check`
Expected: no errors.
Run: `uv run python manage.py collectstatic --noinput -v0` then check `static/` is regenerated (and gitignored from Task 0.2).

- [ ] **Step 5: Commit**

```bash
git add crc/settings.py
git commit -m "chore: env-driven settings, STORAGES dict, doc comments -> Django 6.1"
```

### Task 0.5: Remove Star Admin / jQuery / unused frontend assets

**Files:**

- Delete: `crc/static/css/style.css`, `crc/static/css/vendor.bundle.base.css`, `crc/static/css/themify-icons.css`, `crc/static/fonts/themify.*`
- Delete: `crc/static/js/vendor.bundle.base.js`, `crc/static/js/dashboard.js`, `crc/static/js/chart.js`, `crc/static/js/documentation.js`, `crc/static/js/file-upload.js`, `crc/static/js/tabs.js`, `crc/static/js/tooltips.js`, `crc/static/js/jquery.cookie.js`, `crc/static/js/off-canvas.js`, `crc/static/js/hoverable-collapse.js`, `crc/static/js/template.js`, `crc/static/js/todolist.js`
- Keep: `crc/static/bootstrap/`, `crc/static/img/`

**Interfaces:** Produces a minimal asset set (Bootstrap + logos only). `templates/base.html` will be rewritten in Phase 4 to not reference the deleted files; until then the site will be unstyled — **this is expected and acceptable between Task 0.5 and Task 4.5**.

- [ ] **Step 1: Delete the assets**

```bash
rm -f crc/static/css/style.css crc/static/css/vendor.bundle.base.css crc/static/css/themify-icons.css
rm -f crc/static/fonts/themify.eot crc/static/fonts/themify.svg crc/static/fonts/themify.ttf crc/static/fonts/themify.woff
rm -f crc/static/js/vendor.bundle.base.js crc/static/js/dashboard.js crc/static/js/chart.js crc/static/js/documentation.js
rm -f crc/static/js/file-upload.js crc/static/js/tabs.js crc/static/js/tooltips.js crc/static/js/jquery.cookie.js
rm -f crc/static/js/off-canvas.js crc/static/js/hoverable-collapse.js crc/static/js/template.js crc/static/js/todolist.js
rmdir crc/static/fonts 2>/dev/null || true
```

- [ ] **Step 2: Verify Bootstrap still present**

Run: `ls crc/static/bootstrap/css/bootstrap.min.css crc/static/bootstrap/js/bootstrap.bundle.min.js`
Expected: both files listed.

- [ ] **Step 3: Commit**

```bash
git add -A crc/static/
git commit -m "chore: remove Star Admin CSS, jQuery bundle, and unused JS/chart assets"
```

### Task 0.6: Rewrite README

**Files:**

- Modify: `README.md`

**Interfaces:** Produces accurate setup docs.

- [ ] **Step 1: Rewrite `README.md`** with: project description (cable-reel winding calculator), requirements (Python 3.13+, Django 6.1), uv setup (`uv sync`, `uv run python manage.py migrate`, `uv run python manage.py runserver`), pip alternative (`pip install -r requirements.txt`), the 4 supported languages, light/dark theme note, and the MIT license. Mention `collectstatic` for production.

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: rewrite README for Django 6.1 + uv + i18n/themes"
```

---

## Phase 1 — Formula & Critical Backend Bugs (TDD)

> Pure logic lives in `app/calc.py` so it is testable without Django HTTP. The
> view calls it. Until Phase 2 the view still writes to the old `TextField`
> model columns; Phase 2 switches storage to `CableLineItem`.

### Task 1.1: Create `app/calc.py` with the guarded winding formula

**Files:**

- Create: `app/calc.py`
- Create: `app/tests/__init__.py` (empty)

**Interfaces:**

- Produces: `compute_line(line, reels, settings, transport) -> LineResult` and helpers `winding_length(reel, cable_diameter, margin_mm, packing) -> float`, `choose_reel(...)`, `reel_count_and_len(order_len, l_per_reel) -> tuple[int,float]`.
- `LineResult` is a `dataclass`: `reel: ReelsList | None`, `reel_len: float`, `reel_num: int`, `netto_1: float`, `brutto_1: float`, `netto_all: float`, `brutto_all: float`, `bending_radius: float`, `warning: str | None`.
- `line` is a duck-typed object with attributes: `cod, name, con_num, order_len, max_len, mass, diameter` (strings/numbers — calc casts).
- `reels` is a list of `ReelsList`-like objects with: `pk, name, diameter, diameter_neck, length_neck, height, mass, max_load, width`.
- `settings` has: `winding_margin_mm`, `packing_factor`, `bending_radius_multiplier`.

- [ ] **Step 1: Write `app/calc.py`**

```python
"""Pure calculation logic for cable-reel winding.

No Django models are imported here except as type hints — callers pass
plain objects/attrs so this module is unit-testable without the ORM.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


class CalculationError(ValueError):
    """Raised when a cable line cannot be placed on any reel."""


@dataclass
class LineResult:
    reel_pk: int | None
    reel_name: str
    reel_len: float          # m wound on one reel
    reel_num: int            # number of reels needed (>=1)
    netto_1: float           # kg, cable on one reel
    brutto_1: float          # kg, cable + one reel
    netto_all: float         # kg, all cable in the line
    brutto_all: float        # kg, all cable + all reels
    bending_radius: float    # mm
    warning: str | None = None


def winding_length(reel, cable_diameter: float, margin_mm: float, packing: float) -> float:
    """Length (m) of cable that fits on `reel`.

    L = packing * B * (D_wind^2 - d_core^2) / (4 * d_cable^2) * pi / 1000
    where D_wind = reel.diameter - 2*margin, B = reel.length_neck,
    d_core = reel.diameter_neck. All dimensions in mm; result in metres.
    """
    d_cable = float(cable_diameter)
    if d_cable <= 0:
        raise CalculationError("Cable diameter must be positive")
    if d_cable > float(reel.length_neck):
        raise CalculationError("Cable diameter exceeds reel barrel width")
    d_wind = float(reel.diameter) - 2.0 * float(margin_mm)
    d_core = float(reel.diameter_neck)
    if d_wind <= d_core:
        raise CalculationError("Winding diameter not greater than core diameter")
    b = float(reel.length_neck)
    l_metres = (
        float(packing)
        * b
        * (d_wind ** 2 - d_core ** 2)
        / (4.0 * d_cable ** 2)
        * math.pi
        / 1000.0
    )
    return l_metres


def reel_count_and_len(order_len: float, l_per_reel: float) -> tuple[int, float]:
    """Number of reels (ceil, never 0) and actual metres wound per reel."""
    if l_per_reel <= 0:
        raise CalculationError("Length per reel must be positive")
    count = max(1, math.ceil(float(order_len) / l_per_reel))
    per_reel = float(order_len) / count
    return count, round(per_reel, 3)


def compute_line(line, reels, settings, transport) -> LineResult:
    """Pick the best reel for one cable line and return results + warnings."""
    order_len = float(line.order_len)
    max_len = float(line.max_len)
    mass = float(line.mass)
    cable_d = float(line.diameter)
    margin = float(settings.winding_margin_mm)
    packing = float(settings.packing_factor)

    candidates: list[tuple[float, object]] = []  # (length, reel)
    for reel in reels:
        try:
            l = winding_length(reel, cable_d, margin, packing)
        except CalculationError:
            continue
        if l <= max_len and l > 0:
            candidates.append((l, reel))

    if not candidates:
        raise CalculationError(
            "No reel can hold this cable within the max production length"
        )

    # Choose the reel that holds the most cable (fewest reels).
    best_len, reel = max(candidates, key=lambda t: t[0])
    reel_num, reel_len = reel_count_and_len(order_len, best_len)

    netto_1 = round(reel_len * mass, 2)
    brutto_1 = round(netto_1 + float(reel.mass), 2)
    netto_all = round(order_len * mass, 2)
    brutto_all = round(netto_all + float(reel.mass) * reel_num, 2)
    bending = round(cable_d * float(settings.bending_radius_multiplier), 2)

    warnings = []
    if brutto_1 > float(reel.max_load) > 0:
        warnings.append("Reel max load exceeded")
    if transport and float(transport.max_load) > 0 and brutto_all > float(transport.max_load):
        warnings.append("Transport max load exceeded")
    if cable_d > float(reel.width):
        warnings.append("Cable wider than reel flange width")

    return LineResult(
        reel_pk=reel.pk,
        reel_name=reel.name,
        reel_len=reel_len,
        reel_num=reel_num,
        netto_1=netto_1,
        brutto_1=brutto_1,
        netto_all=netto_all,
        brutto_all=brutto_all,
        bending_radius=bending,
        warning="; ".join(warnings) if warnings else None,
    )
```

- [ ] **Step 2: Create empty `app/tests/__init__.py`**

- [ ] **Step 3: Commit (test file comes in Task 1.2)**

```bash
git add app/calc.py app/tests/__init__.py
git commit -m "feat: add pure, guarded cable-winding calculation module"
```

### Task 1.2: Unit-test the formula (TDD — write failing then passing)

**Files:**

- Create: `app/tests/test_calc.py`

**Interfaces:** Consumes `app/calc.compute_line`, `winding_length`, `reel_count_and_len`, `CalculationError`.

- [ ] **Step 1: Write the tests**

```python
import math
from dataclasses import dataclass
from django.test import SimpleTestCase

from app.calc import (
    CalculationError,
    LineResult,
    compute_line,
    reel_count_and_len,
    winding_length,
)


@dataclass
class FakeReel:
    pk: int = 1
    name: str = "R1000"
    diameter: int = 1000
    diameter_neck: int = 500
    length_neck: int = 600
    height: int = 250
    width: int = 600
    mass: int = 120
    max_load: int = 2000


@dataclass
class FakeLine:
    cod: str = "N2XH"
    name: str = "2x2.5"
    con_num: int = 2
    order_len: str = "5000"
    max_len: str = "3000"
    mass: str = "1.52"
    diameter: str = "14.3"


@dataclass
class FakeSettings:
    winding_margin_mm: float = 50.0
    packing_factor: float = 0.93
    bending_radius_multiplier: float = 10.0


@dataclass
class FakeTransport:
    max_load: int = 10000


class WindingLengthTests(SimpleTestCase):
    def test_positive_length(self):
        L = winding_length(FakeReel(), 14.3, 50.0, 0.93)
        self.assertGreater(L, 0)

    def test_zero_diameter_raises(self):
        with self.assertRaises(CalculationError):
            winding_length(FakeReel(), 0, 50.0, 0.93)

    def test_cable_wider_than_barrel_raises(self):
        with self.assertRaises(CalculationError):
            winding_length(FakeReel(), 999, 50.0, 0.93)

    def test_wind_leq_core_raises(self):
        # margin so large that D_wind <= core
        with self.assertRaises(CalculationError):
            winding_length(FakeReel(), 14.3, 1000.0, 0.93)


class ReelCountTests(SimpleTestCase):
    def test_ceil_never_zero(self):
        self.assertEqual(reel_count_and_len(400, 1000), (1, 400.0))

    def test_rounds_up(self):
        count, per = reel_count_and_len(5000, 3000)
        self.assertEqual(count, 2)
        self.assertAlmostEqual(per, 2500.0)

    def test_exact(self):
        self.assertEqual(reel_count_and_len(3000, 1000), (3, 1000.0))


class ComputeLineTests(SimpleTestCase):
    def test_happy_path(self):
        r = compute_line(FakeLine(), [FakeReel()], FakeSettings(), FakeTransport())
        self.assertIsInstance(r, LineResult)
        self.assertEqual(r.reel_pk, 1)
        self.assertGreaterEqual(r.reel_num, 1)
        self.assertGreater(r.netto_all, 0)
        self.assertAlmostEqual(r.netto_all, 5000 * 1.52, places=2)

    def test_no_reel_fits_raises(self):
        # max_len smaller than any reel's capacity -> no candidates
        line = FakeLine(max_len="1")
        with self.assertRaises(CalculationError):
            compute_line(line, [FakeReel()], FakeSettings(), FakeTransport())

    def test_max_load_warning(self):
        line = FakeLine(order_len="100000", max_len="1000000")
        r = compute_line(line, [FakeReel(max_load=1)], FakeSettings(), FakeTransport(max_load=1))
        self.assertIsNotNone(r.warning)
        self.assertIn("load", r.warning.lower())
```

- [ ] **Step 2: Run tests — expect PASS** (calc already implemented in 1.1; if any fail, fix `calc.py` not the test)

Run: `uv run python manage.py test app.tests.test_calc -v2`
Expected: all tests pass.

- [ ] **Step 3: Commit**

```bash
git add app/tests/test_calc.py
git commit -m "test: unit tests for winding formula and guards"
```

### Task 1.3: Wire `calc.py` into `CableCalView` (still old model); remove debug

**Files:**

- Modify: `app/views.py`

**Interfaces:** Consumes `app.calc.compute_line`. Still writes newline-joined TextFields until Phase 2 (kept for compatibility with existing templates/DB).

- [ ] **Step 1: Rewrite the `form_valid` body of `CableCalView`** to use `compute_line` and drop `print()`, the redundant `get_object_or_404(TransportList...)`, and the manual formula. Keep the old TextField storage for now. Replace the entire `form_valid` method with:

```python
    def form_valid(self, form):
        from .calc import CalculationError, compute_line
        from .models import CalculationSettings

        model = form.save(commit=False)
        settings = CalculationSettings.get_solo()
        transport = form.cleaned_data["transport"]

        cods = self.request.POST.getlist("cod")
        names = self.request.POST.getlist("name")
        order_lens = self.request.POST.getlist("order_len")
        masses = self.request.POST.getlist("mass")
        diameters = self.request.POST.getlist("diameter")
        con_nums = self.request.POST.getlist("con_num")
        max_lens = self.request.POST.getlist("max_len")

        reels = list(ReelsList.objects.all())
        rows = zip(cods, names, order_lens, masses, diameters, con_nums, max_lens)

        Line = type("Line", (), {})  # lightweight attr bag
        out = []
        errors = []
        for i, (cod, name, olen, mass, dia, con, mlen) in enumerate(rows):
            line = Line()
            line.cod, line.name, line.con_num = cod, name, con
            line.order_len, line.max_len, line.mass, line.diameter = olen, mlen, mass, dia
            try:
                r = compute_line(line, reels, settings, transport)
                out.append((r.reel_name, r.reel_num, r.reel_len,
                            r.netto_1, r.brutto_1, r.netto_all, r.brutto_all,
                            r.bending_radius, r.warning))
            except CalculationError as e:
                errors.append(f"Row {i + 1}: {e}")

        if errors:
            from django.contrib import messages
            for e in errors:
                messages.error(self.request, e)
            return self.form_invalid(form)

        def _join(idx):
            return "\n".join(str(row[idx]) for row in out)

        with transaction.atomic():
            self.object = CableCal.objects.create(
                order_num=form.cleaned_data["order_num"],
                transport=transport,
                cod=_join(0), name="\n".join(names),
                order_len="\n".join(order_lens), mass="\n".join(masses),
                diameter="\n".join(diameters), con_num="\n".join(con_nums),
                max_len="\n".join(max_lens),
                reel_name=_join(0 + 0),  # reel_name is index 0 in out tuple
                reel_num=_join(1), reel_len=_join(2),
                netto_1=_join(3), brutto_1=_join(4),
                netto_all=_join(5), brutto_all=_join(6),
                bending_radius=_join(7),
            )
        return super().form_valid(form)
```

> NOTE: the `out` tuple ordering is `(reel_name, reel_num, reel_len, netto_1, brutto_1, netto_all, brutto_all, bending_radius, warning)`. Adjust `_join` indices to match exactly: `reel_name=_join(0)`, `reel_num=_join(1)`, `reel_len=_join(2)`, `netto_1=_join(3)`, `brutto_1=_join(4)`, `netto_all=_join(5)`, `brutto_all=_join(6)`, `bending_radius=_join(7)`. The `warning` (index 8) is not stored on the old model — dropped until Phase 2.

- [ ] **Step 2: Fix `ReelType.get_absolute_url` crash** in `app/models.py` — replace:

```python
    def get_absolute_url(self):
        return reverse('reels_list', kwargs={"pk": self.pk})
```

with:

```python
    def get_absolute_url(self):
        return reverse('reel_type_list')
```

(Add a `reel_type_list` URL in Task 1.4, or point it at `reels_list` with no kwargs: `return reverse('reels_list')`. Use the latter to avoid a new view: `return reverse("reels_list")`.)

- [ ] **Step 3: Remove the dead `clean_title` methods** from all three forms in `app/forms.py` (they are nested inside `Meta` and broken). Delete each:

```python
        def clean_title(self):
            name = self.clean_title["name"]
            return name
```

(and the `order_num` variant). Also remove inline `style="..."` from all widget `attrs` — replace with `"class": "form-control"` (and `"class": "form-select"` for Select widgets). Keep only the `class` attr. This unblocks theming.

- [ ] **Step 4: Remove wildcard imports** in `app/views.py`: change `from .forms import *` → `from .forms import CableCalForm, ReelsListForm, TransportListForm` and `from .models import *` → `from .models import CableCal, ReelsList, TransportList, CalculationSettings`. (`CalculationSettings` is added in Task 2.2; if running before 2.2, import it lazily inside `form_valid` as shown.)

- [ ] **Step 5: Verify**

Run: `uv run python manage.py check && uv run python manage.py test app.tests.test_calc`
Expected: no errors, calc tests still pass.

- [ ] **Step 6: Commit**

```bash
git add app/views.py app/forms.py app/models.py
git commit -m "fix: use guarded calc module in view; remove debug/dead code; fix ReelType URL"
```

### Task 1.4: Normalize URL definitions

**Files:**

- Modify: `app/urls.py`

**Interfaces:** Produces consistent trailing slashes; fixes `transport_list_` typo.

- [ ] **Step 1: Rewrite `app/urls.py`** with consistent `/`-terminated paths and app namespace:

```python
from django.urls import path

from .views import (
    CableCalDel, CableCalDetail, CableCalList, CableCalView,
    ReelsListCreate, ReelsListDel, ReelsListDetail, ReelsListView,
    TransportListCreate, TransportListDel, TransportListDetail, TransportListView,
)

app_name = "app"

urlpatterns = [
    path("", CableCalView.as_view(), name="cable_cal"),
    path("cables/", CableCalList.as_view(), name="cable_list"),
    path("cables/<int:pk>/", CableCalDetail.as_view(), name="cable_detail"),
    path("cables/<int:pk>/delete/", CableCalDel.as_view(), name="cable_del"),
    path("reels/", ReelsListView.as_view(), name="reels_list"),
    path("reels/<int:pk>/", ReelsListDetail.as_view(), name="reels_list_detail"),
    path("reels/add/", ReelsListCreate.as_view(), name="reels_add"),
    path("reels/<int:pk>/delete/", ReelsListDel.as_view(), name="reels_del"),
    path("transport/", TransportListView.as_view(), name="transport_list"),
    path("transport/<int:pk>/", TransportListDetail.as_view(), name="transport_list_detail"),
    path("transport/add/", TransportListCreate.as_view(), name="transport_add"),
    path("transport/<int:pk>/delete/", TransportListDel.as_view(), name="transport_del"),
]
```

- [ ] **Step 2: Update all template `{% url %}` calls** that referenced old names/paths. Grep and replace:
  - `{% url 'cable_cal' %}` → `{% url 'app:cable_cal' %}`
  - `{% url 'cable_list' %}` → `{% url 'app:cable_list' %}`
  - `{% url 'cable_detail' pk=... %}` → `{% url 'app:cable_detail' pk=... %}`
  - `{% url 'cable_del' pk=... %}` → `{% url 'app:cable_del' pk=... %}`
  - `{% url 'reels_list' %}`, `{% url 'reels_list_detail' %}`, `{% url 'reels_add' %}`, `{% url 'reels_del' pk=... %}`
  - `{% url 'transport_list' %}`, `{% url 'transport_list_detail' %}`, `{% url 'transport_add' %}`, `{% url 'transport_del' pk=... %}`
  - All become `app:<name>`. (`get_absolute_url` in models uses `reverse("app:cable_detail", ...)` etc. — update models accordingly.)

- [ ] **Step 3: Update `models.py` `get_absolute_url`/`reverse` calls** to use the `app:` namespace:
  - `CableCal`: `reverse("app:cable_detail", kwargs={"pk": self.pk})`
  - `ReelsList`: `reverse("app:reels_list_detail", kwargs={"pk": self.pk})`
  - `ReelType`: `reverse("app:reels_list")`
  - `TransportList`: `reverse("app:transport_list_detail", kwargs={"pk": self.pk})`
  - Views: `reverse_lazy("app:cable_list")`, `reverse_lazy("app:reels_list")`, `reverse_lazy("app:transport_list")`.

- [ ] **Step 4: Verify**

Run: `uv run python manage.py check`
Run: `uv run python manage.py test`
Expected: no `NoReverseMatch` errors.

- [ ] **Step 5: Commit**

```bash
git add app/urls.py app/models.py app/views.py app/templates/
git commit -m "refactor: consistent URL schema with app namespace; fix transport_list_ typo"
```

---

## Phase 2 — Data Model Normalization

### Task 2.1: Add `CalculationSettings` singleton model

**Files:**

- Modify: `app/models.py`

**Interfaces:** Produces `CalculationSettings.get_solo()` classmethod returning the single row (created on demand).

- [ ] **Step 1: Add the model** at top of `app/models.py` (after imports, add `from django.utils.translation import gettext_lazy as _`):

```python
class CalculationSettings(models.Model):
    winding_margin_mm = models.FloatField(
        default=50.0, verbose_name=_("Winding margin (mm)"),
        help_text=_("Unwound margin per flange side."),
    )
    packing_factor = models.FloatField(
        default=0.93, verbose_name=_("Packing factor"),
    )
    bending_radius_multiplier = models.FloatField(
        default=10.0, verbose_name=_("Bending radius multiplier (× cable diameter)"),
    )
    use_flange_height = models.BooleanField(
        default=False, verbose_name=_("Use flange height to bound winding"),
    )

    class Meta:
        verbose_name = _("Calculation settings")
        verbose_name_plural = _("Calculation settings")

    @classmethod
    def get_solo(cls) -> "CalculationSettings":
        obj, _ = cls.objects.get_or_create(pk=1, defaults={"pk": 1})
        return obj

    def __str__(self):
        return "Calculation settings"
```

- [ ] **Step 2: Make migration**

Run: `uv run python manage.py makemigrations app --name calcsettings`
Expected: migration created for `CalculationSettings`.

- [ ] **Step 3: Migrate & verify**

Run: `uv run python manage.py migrate app`
Run: `uv run python manage.py shell -c "from app.models import CalculationSettings; print(CalculationSettings.get_solo().packing_factor)"`
Expected: `0.93`.

- [ ] **Step 4: Commit**

```bash
git add app/models.py app/migrations/
git commit -m "feat: add CalculationSettings singleton model"
```

### Task 2.2: Add `CableLineItem` model; mark old `CableCal` columns nullable

**Files:**

- Modify: `app/models.py`
- Create: `app/migrations/0004_calcsettings_lineitem.py` (generated)

**Interfaces:**

- Produces `CableLineItem` (FK→`CableCal`, ordered by `position`).
- `CableCal` keeps old TextField columns **nullable/blank** during the transition (removed in Task 2.5 step after data migration).

- [ ] **Step 1: Add `CableLineItem`** to `app/models.py`. Use `DecimalField` for numerics:

```python
from decimal import Decimal


class CableLineItem(models.Model):
    cable_cal = models.ForeignKey(
        CableCal, related_name="line_items", on_delete=models.CASCADE,
        verbose_name=_("Calculation"),
    )
    position = models.PositiveIntegerField(default=0, verbose_name=_("Position"))
    cod = models.CharField(max_length=100, blank=True, verbose_name=_("Cable code"))
    name = models.CharField(max_length=200, blank=True, verbose_name=_("Cable name"))
    con_num = models.PositiveIntegerField(default=1, verbose_name=_("Conductor count"))
    order_len = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0"),
        verbose_name=_("Order length (m)"),
    )
    max_len = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0"),
        verbose_name=_("Max production length (m)"),
    )
    mass = models.DecimalField(
        max_digits=8, decimal_places=3, default=Decimal("0"),
        verbose_name=_("Cable mass (kg/m)"),
    )
    diameter = models.DecimalField(
        max_digits=6, decimal_places=2, default=Decimal("0"),
        verbose_name=_("Cable outer diameter (mm)"),
    )
    # results
    reel = models.ForeignKey(
        ReelsList, null=True, blank=True, on_delete=models.PROTECT,
        verbose_name=_("Chosen reel"),
    )
    reel_len = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal("0"),
        verbose_name=_("Length per reel (m)"),
    )
    reel_num = models.PositiveIntegerField(default=0, verbose_name=_("Reel count"))
    netto_1 = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"),
        verbose_name=_("Netto 1 reel (kg)"),
    )
    brutto_1 = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"),
        verbose_name=_("Brutto 1 reel (kg)"),
    )
    netto_all = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"),
        verbose_name=_("Netto total (kg)"),
    )
    brutto_all = models.DecimalField(
        max_digits=12, decimal_places=2, default=Decimal("0"),
        verbose_name=_("Brutto total (kg)"),
    )
    bending_radius = models.DecimalField(
        max_digits=8, decimal_places=2, default=Decimal("0"),
        verbose_name=_("Bending radius (mm)"),
    )
    warning = models.TextField(blank=True, default="", verbose_name=_("Warning"))

    class Meta:
        verbose_name = _("Cable line item")
        verbose_name_plural = _("Cable line items")
        ordering = ["position"]

    def __str__(self):
        return f"{self.name} ({self.cod})"
```

- [ ] **Step 2: Add `margin_override`/`packing_override` to `CableCal`** (nullable):

```python
    margin_override = models.FloatField(
        null=True, blank=True, verbose_name=_("Winding margin override (mm)"),
    )
    packing_override = models.FloatField(
        null=True, blank=True, verbose_name=_("Packing factor override"),
    )
```

- [ ] **Step 3: Add constraints** to `ReelsList.Meta`:

```python
        constraints = [
            models.CheckConstraint(
                check=models.Q(diameter__gt=models.F("diameter_neck")),
                name="reel_diameter_gt_neck",
            ),
            models.CheckConstraint(check=models.Q(max_load__gt=0), name="reel_max_load_pos"),
            models.CheckConstraint(check=models.Q(length_neck__gt=0), name="reel_length_neck_pos"),
        ]
```

- [ ] **Step 4: Make old `CableCal` TextField columns blankable** (set `blank=True` already true for results; for inputs add `blank=True`) so the data migration can proceed. (No schema change needed if already `blank=True`; just ensure.)

- [ ] **Step 5: Make migration**

Run: `uv run python manage.py makemigrations app --name lineitem`
Expected: migration creates `CableLineItem`, adds overrides, adds constraints.

- [ ] **Step 6: Migrate**

Run: `uv run python manage.py migrate app`

> **Guard:** if the `CheckConstraint` on existing `ReelsList` rows fails (e.g. a reel with `max_load<=0`), the migration will error. Inspect data first: `uv run python manage.py shell -c "from app.models import ReelsList; print([r.name for r in ReelsList.objects.all() if r.max_load<=0 or r.diameter<=r.diameter_neck or r.length_neck<=0])"`. Fix or relax the constraint if needed before migrating.

- [ ] **Step 7: Commit**

```bash
git add app/models.py app/migrations/
git commit -m "feat: add CableLineItem model, calc overrides, reel constraints"
```

### Task 2.3: Formset for line items; clean forms

**Files:**

- Modify: `app/forms.py`

**Interfaces:** Produces `CableLineItemForm` (ModelForm) and `CableLineItemFormSet` (formset_factory). `CableCalForm` reduced to header fields only (`order_num`, `transport`, optional overrides).

- [ ] **Step 1: Rewrite `app/forms.py`** — remove inline styles (already done in 1.3), use `form-control`/`form-select`, `gettext_lazy`, define formset:

```python
from django import forms
from django.forms import formset_factory, modelformset_factory
from django.utils.translation import gettext_lazy as _

from .models import CableCal, CableLineItem, ReelsList, TransportList


class CableCalForm(forms.ModelForm):
    class Meta:
        model = CableCal
        fields = ["order_num", "transport", "margin_override", "packing_override"]
        widgets = {
            "order_num": forms.TextInput(attrs={"class": "form-control"}),
            "transport": forms.Select(attrs={"class": "form-select"}),
            "margin_override": forms.NumberInput(attrs={"class": "form-control", "step": "0.1"}),
            "packing_override": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }


class CableLineItemForm(forms.ModelForm):
    class Meta:
        model = CableLineItem
        fields = ["cod", "name", "con_num", "order_len", "max_len", "mass", "diameter"]
        widgets = {
            "cod": forms.TextInput(attrs={"class": "form-control"}),
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "con_num": forms.NumberInput(attrs={"class": "form-control"}),
            "order_len": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "max_len": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "mass": forms.NumberInput(attrs={"class": "form-control", "step": "0.001"}),
            "diameter": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
        }


CableLineItemFormSet = formset_factory(
    CableLineItemForm, extra=1, can_delete=True,
)


class ReelsListForm(forms.ModelForm):
    class Meta:
        model = ReelsList
        fields = ["name", "height", "width", "diameter", "diameter_neck",
                  "length_neck", "reel_type", "mass", "max_load"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "height": forms.NumberInput(attrs={"class": "form-control"}),
            "width": forms.NumberInput(attrs={"class": "form-control"}),
            "diameter": forms.NumberInput(attrs={"class": "form-control"}),
            "diameter_neck": forms.NumberInput(attrs={"class": "form-control"}),
            "length_neck": forms.NumberInput(attrs={"class": "form-control"}),
            "reel_type": forms.Select(attrs={"class": "form-select"}),
            "mass": forms.NumberInput(attrs={"class": "form-control"}),
            "max_load": forms.NumberInput(attrs={"class": "form-control"}),
        }


class TransportListForm(forms.ModelForm):
    class Meta:
        model = TransportList
        fields = ["name", "length", "width", "height", "max_load"]
        widgets = {
            "name": forms.TextInput(attrs={"class": "form-control"}),
            "length": forms.NumberInput(attrs={"class": "form-control"}),
            "width": forms.NumberInput(attrs={"class": "form-control"}),
            "height": forms.NumberInput(attrs={"class": "form-control"}),
            "max_load": forms.NumberInput(attrs={"class": "form-control"}),
        }
```

- [ ] **Step 2: Verify**

Run: `uv run python manage.py check`
Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add app/forms.py
git commit -m "feat: CableLineItem formset; clean header form; remove inline styles"
```

### Task 2.4: Rewrite `CableCalView` to use formset + line items

**Files:**

- Modify: `app/views.py`

**Interfaces:** Consumes `CableLineItemFormSet`, `compute_line`, `CalculationSettings.get_solo()`. Produces `CableCal` + N `CableLineItem` rows. The template (Phase 4) renders the formset; the old `cable_cal.html` will be updated in Task 4.6. **Until then, the form page will not render the formset correctly — acceptable; the view is tested directly in Task 2.7.**

- [ ] **Step 1: Rewrite `CableCalView`**:

```python
from django.contrib import messages
from django.db import transaction
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, DetailView, ListView, View

from .calc import CalculationError, compute_line
from .forms import CableCalForm, CableLineItemFormSet, ReelsListForm, TransportListForm
from .models import CableCal, CableLineItem, CalculationSettings, ReelsList, TransportList


class CableCalView(View):
    template_name = "app/cable_cal.html"

    def get(self, request):
        return render(request, self.template_name, {
            "form": CableCalForm(),
            "formset": CableLineItemFormSet(),
        })

    def post(self, request):
        form = CableCalForm(request.POST)
        formset = CableLineItemFormSet(request.POST)
        if not (form.is_valid() and formset.is_valid()):
            return render(request, self.template_name, {"form": form, "formset": formset})

        settings = CalculationSettings.get_solo()
        margin = form.cleaned_data.get("margin_override") or settings.winding_margin_mm
        packing = form.cleaned_data.get("packing_override") or settings.packing_factor
        transport = form.cleaned_data["transport"]
        reels = list(ReelsList.objects.all())

        class _Settings:
            pass
        s = _Settings()
        s.winding_margin_mm = margin
        s.packing_factor = packing
        s.bending_radius_multiplier = settings.bending_radius_multiplier

        results = []
        errors = []
        for i, lf in enumerate(formset):
            if lf.cleaned_data.get("DELETE"):
                continue
            line = lf.save(commit=False)
            try:
                r = compute_line(line, reels, s, transport)
                results.append((lf, r))
            except CalculationError as e:
                errors.append(_("Row %(n)s: %(err)s") % {"n": i + 1, "err": str(e)})

        if errors:
            for e in errors:
                messages.error(request, e)
            return render(request, self.template_name, {"form": form, "formset": formset})

        with transaction.atomic():
            calc = form.save(commit=False)
            calc.margin_override = form.cleaned_data.get("margin_override")
            calc.packing_override = form.cleaned_data.get("packing_override")
            calc.save()
            for pos, (lf, r) in enumerate(results):
                item = lf.save(commit=False)
                item.cable_cal = calc
                item.position = pos
                item.reel = ReelsList.objects.filter(pk=r.reel_pk).first()
                item.reel_len = r.reel_len
                item.reel_num = r.reel_num
                item.netto_1 = r.netto_1
                item.brutto_1 = r.brutto_1
                item.netto_all = r.netto_all
                item.brutto_all = r.brutto_all
                item.bending_radius = r.bending_radius
                item.warning = r.warning or ""
                item.save()
        return redirect(calc.get_absolute_url())
```

> Remove the old `CableCalView(FormView)` entirely. Update the imports block at top of `views.py` to the explicit list shown (drop wildcard imports).

- [ ] **Step 2: Keep the other class-based views** (`CableCalList`, `CableCalDetail`, `CableCalDel`, `ReelsListView`, etc.) but update `success_url` `reverse_lazy` calls to the `app:` namespace. `CableCalDel` template name → `app/cable_cal_confirm_delete.html` (rename happens in Phase 4; keep old name working until then by leaving template_name as `app/cable_cal_del.html` and renaming in Task 4.9).

- [ ] **Step 3: Verify**

Run: `uv run python manage.py check`
Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add app/views.py
git commit -m "feat: formset-driven CableCalView writes CableLineItem rows"
```

### Task 2.5: Data migration — split old `CableCal` TextFields into `CableLineItem` rows

**Files:**

- Create: `app/migrations/0005_split_cablecal_to_lineitems.py`

**Interfaces:** Consumes the 3 existing `CableCal` records (newline-joined fields). Produces `CableLineItem` rows preserving computed results. Idempotent-ish (only creates items for cables that don't yet have line items).

- [ ] **Step 1: Create the data migration** (generate stub first):

Run: `uv run python manage.py makemigrations app --empty --name split_cablecal_to_lineitems`

- [ ] **Step 2: Fill the migration** with `RunPython`:

```python
from django.db import migrations


def split(apps, schema_editor):
    CableCal = apps.get_model("app", "CableCal")
    CableLineItem = apps.get_model("app", "CableLineItem")
    ReelsList = apps.get_model("app", "ReelsList")
    from decimal import Decimal

    def rows(field):
        return (field or "").split("\n") if field else []

    for calc in CableCal.objects.all():
        if calc.line_items.exists():
            continue  # already migrated
        cods = rows(calc.cod); names = rows(calc.name)
        reel_names = rows(calc.reel_name); reel_nums = rows(calc.reel_num)
        reel_lens = rows(calc.reel_len); netto1 = rows(calc.netto_1)
        brutto1 = rows(calc.brutto_1); netto_all = rows(calc.netto_all)
        brutto_all = rows(calc.brutto_all); bend = rows(calc.bending_radius)
        masses = rows(calc.mass); diams = rows(calc.diameter)
        cons = rows(calc.con_num); ols = rows(calc.order_len); mls = rows(calc.max_len)
        n = max(len(cods), len(names), len(ols))
        for i in range(n):
            def g(lst, i, cast=str, default=""):
                v = lst[i] if i < len(lst) else default
                try:
                    return cast(v) if v not in ("", None) else (cast(0) if cast in (int, Decimal) else "")
                except (ValueError, TypeError):
                    return cast(0) if cast in (int, Decimal) else ""
            rname = g(reel_names, i)
            reel = ReelsList.objects.filter(name=rname).first() if rname else None
            CableLineItem.objects.create(
                cable_cal=calc, position=i,
                cod=g(cods, i), name=g(names, i),
                con_num=g(cons, i, int, 1),
                order_len=g(ols, i, Decimal),
                max_len=g(mls, i, Decimal),
                mass=g(masses, i, Decimal),
                diameter=g(diams, i, Decimal),
                reel=reel,
                reel_len=g(reel_lens, i, Decimal),
                reel_num=g(reel_nums, i, int),
                netto_1=g(netto1, i, Decimal),
                brutto_1=g(brutto1, i, Decimal),
                netto_all=g(netto_all, i, Decimal),
                brutto_all=g(brutto_all, i, Decimal),
                bending_radius=g(bend, i, Decimal),
                warning="",
            )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("app", "0004_calcsettings_lineitem"),
    ]
    operations = [
        migrations.RunPython(split, noop),
    ]
```

- [ ] **Step 3: Backup the DB, then migrate**

```bash
cp db.sqlite3 db.sqlite3.bak
uv run python manage.py migrate app
```

- [ ] **Step 4: Verify the 3 records split correctly**

Run:

```
uv run python manage.py shell -c "from app.models import CableCal, CableLineItem; [print(c.order_num, c.line_items.count()) for c in CableCal.objects.all()]"
```

Expected: each of the 3 `CableCal` has `line_items.count() >= 1`.

- [ ] **Step 5: Remove the old TextField columns** in a follow-up migration only AFTER confirming the split. Add to `app/models.py`: delete the fields `cod, name, mass, diameter, con_num, order_len, max_len, reel_name, reel_type, reel_num, reel_len, bending_radius, netto_1, brutto_1, netto_all, brutto_all` from `CableCal`. Make migration (`makemigrations app --name remove_cablecal_legacy_columns`) and migrate.

- [ ] **Step 6: Verify templates still render** — `cable_cal_detail.html` currently reads `cable_cal.cod|linebreaks` etc. These break after column removal. **Phase 4 rewrites these templates** to use `cable_cal.line_items`. To keep the site green between Phase 2 and Phase 4, defer Step 5 (column removal) until Task 4.8 is done. **Order adjustment:** execute Task 2.5 Steps 1–4 now; execute Step 5 (column removal migration) at the end of Phase 4 (Task 4.12).

- [ ] **Step 7: Commit (Steps 1–4 only)**

```bash
git add app/migrations/0005_split_cablecal_to_lineitems.py
git commit -m "migrate: split CableCal legacy text fields into CableLineItem rows"
```

### Task 2.6: Model & constraint tests

**Files:**

- Create: `app/tests/test_models.py`

**Interfaces:** Consumes `CalculationSettings`, `CableLineItem`, `ReelsList`, constraints.

- [ ] **Step 1: Write tests**

```python
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from app.models import CableCal, CableLineItem, CalculationSettings, ReelsList, TransportList


class CalculationSettingsTests(TestCase):
    def test_solo_creates_one_row(self):
        a = CalculationSettings.get_solo()
        b = CalculationSettings.get_solo()
        self.assertEqual(a.pk, b.pk)
        self.assertEqual(CalculationSettings.objects.count(), 1)
        self.assertEqual(a.packing_factor, 0.93)


class CableLineItemTests(TestCase):
    def setUp(self):
        self.transport = TransportList.objects.create(
            name="TIR", length=13000, width=2450, height=2700, max_load=24000)
        self.calc = CableCal.objects.create(order_num="ORD-1", transport=self.transport)

    def test_create_line_item(self):
        item = CableLineItem.objects.create(
            cable_cal=self.calc, position=0, cod="X", name="N2XH 2x2.5",
            order_len="5000", max_len="3000", mass="1.52", diameter="14.3")
        self.assertEqual(str(item), "N2XH 2x2.5 (X)")
        self.assertEqual(self.calc.line_items.count(), 1)


class ReelsListConstraintTests(TestCase):
    def test_diameter_must_exceed_neck(self):
        r = ReelsList(name="bad", height=100, width=100, diameter=100,
                      diameter_neck=200, length_neck=100, mass=10, max_load=100)
        with self.assertRaises(ValidationError):
            r.full_clean()

    def test_max_load_positive(self):
        r = ReelsList(name="bad2", height=100, width=100, diameter=300,
                      diameter_neck=100, length_neck=100, mass=10, max_load=0)
        with self.assertRaises(ValidationError):
            r.full_clean()
```

- [ ] **Step 2: Run tests**

Run: `uv run python manage.py test app.tests.test_models -v2`
Expected: all pass. (SQLite does not enforce `CheckConstraint` at the DB level by default in older versions, but `full_clean()` validates via Django model validation; the test uses `full_clean()` so it works regardless.)

- [ ] **Step 3: Commit**

```bash
git add app/tests/test_models.py
git commit -m "test: CalculationSettings singleton, CableLineItem, reel constraints"
```

### Task 2.7: View tests (formset submission, error path)

**Files:**

- Create: `app/tests/test_views.py`

**Interfaces:** Consumes `CableCalView`, `CalculationSettings`, a fixture `ReelsList`.

- [ ] **Step 1: Write tests**

```python
from decimal import Decimal
from django.test import TestCase
from django.urls import reverse

from app.models import CableCal, CableLineItem, CalculationSettings, ReelsList, TransportList


def make_reel(**kw):
    defaults = dict(name="R1000", height=250, width=600, diameter=1000,
                    diameter_neck=500, length_neck=600, mass=120, max_load=2000)
    defaults.update(kw)
    return ReelsList.objects.create(**defaults)


class CableCalViewTests(TestCase):
    def setUp(self):
        CalculationSettings.get_solo()
        self.reel = make_reel()
        self.transport = TransportList.objects.create(
            name="TIR", length=13000, width=2450, height=2700, max_load=24000)

    def _post_data(self, lines):
        data = {
            "order_num": "ORD-T1",
            "transport": self.transport.pk,
            "form-TOTAL_FORMS": str(len(lines)),
            "form-INITIAL_FORMS": "0",
            "form-MIN_NUM_FORMS": "1",
            "form-MAX_NUM_FORMS": "100",
        }
        for i, ln in enumerate(lines):
            for k, v in ln.items():
                data[f"form-{i}-{k}"] = v
        return data

    def test_create_with_one_line(self):
        data = self._post_data([{
            "cod": "X", "name": "N2XH 2x2.5", "con_num": "2",
            "order_len": "5000", "max_len": "3000", "mass": "1.52", "diameter": "14.3",
        }])
        resp = self.client.post(reverse("app:cable_cal"), data)
        self.assertEqual(resp.status_code, 302)
        calc = CableCal.objects.get(order_num="ORD-T1")
        self.assertEqual(calc.line_items.count(), 1)
        item = calc.line_items.first()
        self.assertEqual(item.reel_num, 2)  # ceil(5000/~3000)
        self.assertIsNotNone(item.reel)

    def test_no_reel_fits_shows_error(self):
        # max_len too small for the reel
        data = self._post_data([{
            "cod": "X", "name": "big", "con_num": "2",
            "order_len": "10", "max_len": "1", "mass": "1", "diameter": "14.3",
        }])
        resp = self.client.post(reverse("app:cable_cal"), data)
        self.assertEqual(resp.status_code, 200)  # re-renders with error
        self.assertFalse(CableCal.objects.filter(order_num="ORD-T1").exists())
```

> The exact `reel_num` assertion (`2`) depends on the reel's computed capacity for `diameter=14.3`. Before finalizing Step 2, run the formula by hand for the fixture reel (margin 50, packing 0.93): `L = 0.93 * 600 * ((900)^2 - 500^2) / (4 * 14.3^2) * pi / 1000`. Compute it and set the expected `reel_num = ceil(5000 / L)`. Adjust the assertion to the real value — do not leave a guessed number.

- [ ] **Step 2: Compute the expected capacity and fix the assertion**

Run:

```bash
uv run python -c "import math; L=0.93*600*((900)**2-500**2)/(4*14.3**2)*math.pi/1000; print('L=',round(L,3),'reels=',-(-5000//int(L)) if int(L) else 'n/a')"
```

Use the printed `reels` value in the assertion (use `math.ceil` semantics). Update `self.assertEqual(item.reel_num, <value>)`.

- [ ] **Step 3: Run tests**

Run: `uv run python manage.py test app.tests.test_views -v2`
Expected: all pass.

- [ ] **Step 4: Commit**

```bash
git add app/tests/test_views.py
git commit -m "test: formset submission creates line items; no-fit error path"
```

---

## Phase 3 — Internationalization (en/az/ru/tr)

### Task 3.1: Wire i18n settings

**Files:**

- Modify: `crc/settings.py`

**Interfaces:** Produces `LANGUAGES`, `LOCALE_PATHS`, `LANGUAGE_CODE`, middleware order.

- [ ] **Step 1: Add i18n settings** — replace the Internationalization block:

```python
# Internationalization
# https://docs.djangoproject.com/en/6.1/topics/i18n/

from django.utils.translation import gettext_lazy as _

LANGUAGES = [
    ("en", _("English")),
    ("az", _("Azərbaycanca")),
    ("ru", _("Русский")),
    ("tr", _("Türkçe")),
]

LANGUAGE_CODE = "en"

TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
DATETIME_FORMAT = "%m/%d/%Y"

LOCALE_PATHS = [BASE_DIR / "locale"]
```

- [ ] **Step 2: Add `LocaleMiddleware`** to `MIDDLEWARE` — insert `"django.middleware.locale.LocaleMiddleware",` **after** `SessionMiddleware` and **before** `CommonMiddleware`:

```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
```

- [ ] **Step 3: Verify**

Run: `uv run python manage.py check`
Expected: no errors.

- [ ] **Step 4: Commit**

```bash
git add crc/settings.py
git commit -m "feat(i18n): LANGUAGES, LOCALE_PATHS, LocaleMiddleware"
```

### Task 3.2: URL routing with `i18n_patterns`

**Files:**

- Modify: `crc/urls.py`

**Interfaces:** Produces `/en/…`, `/az/…`, `/ru/…`, `/tr/…` prefixes for app URLs; admin prefixed too; `set_language` URL included.

- [ ] **Step 1: Rewrite `crc/urls.py`**:

```python
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("app.urls", namespace="app")),
    prefix_default_language=True,
)
```

> Note: `app/urls.py` already declares `app_name = "app"` (Task 1.4). Passing `namespace="app"` in `include` is redundant with `app_name` and will raise if both define the namespace — **drop `namespace="app"`** and rely on `app_name` from `app/urls.py`. Final: `path("", include("app.urls")),`.

- [ ] **Step 2: Verify resolution**

Run:

```bash
uv run python manage.py shell -c "from django.urls import reverse; print(reverse('app:cable_cal', urlconf='crc.urls'))"
```

Hmm — `i18n_patterns` requires an active language. Simpler: start server and `curl /en/`. Instead verify via check:
Run: `uv run python manage.py check`
Expected: no errors.

- [ ] **Step 3: Commit**

```bash
git add crc/urls.py
git commit -m "feat(i18n): i18n_patterns for app + admin; set_language endpoint"
```

### Task 3.3: Mark model/form/view strings with `gettext_lazy`

**Files:**

- Modify: `app/models.py`, `app/forms.py`, `app/views.py`

**Interfaces:** Produces translatable `verbose_name`/`help_text`/labels/messages. (Models already use `_()` from Task 2.1/2.2; verify all `verbose_name` strings are wrapped.)

- [ ] **Step 1: Audit `app/models.py`** — every `verbose_name="…"` and `help_text="…"` must be `verbose_name=_("…")`. Wrap any remaining bare strings (e.g. the old `CableCal` fields still present until Task 4.12, and `ReelType`/`TransportList`/`ReelsList` fields). Add `from django.utils.translation import gettext_lazy as _` at top (already there from 2.1).

- [ ] **Step 2: Audit `app/forms.py`** — labels: add `labels={"order_num": _("Order number"), …}` to each form's `Meta` if not inferred from model verbose_name (model verbose_name is enough if wrapped; no extra work). Wrap any literal strings in `views.py` messages (e.g. `_("Row %(n)s: %(err)s")` already done in 2.4).

- [ ] **Step 3: Verify**

Run: `uv run python manage.py check && uv run python manage.py test`
Expected: no errors; existing tests pass.

- [ ] **Step 4: Commit**

```bash
git add app/models.py app/forms.py app/views.py
git commit -m "i18n: mark all model/form/view strings with gettext_lazy"
```

### Task 3.4: Mark all template strings; fix `lang` attribute

**Files:**

- Modify: all `app/templates/app/*.html` and `templates/base.html`

**Interfaces:** Produces templates using `{% load i18n %}` and `{% trans %}`/`{% blocktrans %}`; `<html lang="{{ LANGUAGE_CODE }}">`.

> This task marks strings **in the current (Star Admin-era) templates**. Phase 4 rewrites the templates, but marking now means the `.po` extraction (Task 3.5) captures every string, and Phase 4 can reuse the same msgids. To avoid double work, **consider deferring 3.4 until after the Phase 4 rewrite** and marking the new templates directly. **Decision: merge 3.4 into Phase 4** — each Phase 4 template task includes `{% trans %}` marking. Skip 3.4 as a standalone task; proceed to 3.5 only after Phase 4.

- [ ] **Step 1: Skip (merged into Phase 4).** Note in commit messages of Phase 4 tasks that i18n marking is included.

### Task 3.5: Extract & compile translations for 4 locales

**Files:**

- Create: `locale/en/LC_MESSAGES/django.po`, `locale/az/LC_MESSAGES/django.po`, `locale/ru/LC_MESSAGES/django.po`, `locale/tr/LC_MESSAGES/django.po` (+ `.mo` compiled, gitignored)

**Interfaces:** Runs **after Phase 4** so all template strings exist. Produces committed `.po` files with full translations.

- [ ] **Step 1: Create locale dirs & extract** (run after Phase 4 templates are done):

```bash
mkdir -p locale
uv run python manage.py makemessages -l en -l az -l ru -tr --ignore=static --ignore=.venv
```

- [ ] **Step 2: Fill translations** in each `.po` file. English: copy msgid as msgstr (or leave blank — Django falls back to msgid). For `az`, `ru`, `tr`: provide translations for every msgid. Key strings to translate (non-exhaustive): "Calculation", "Calculation history", "Reel list", "Transport list", "Order number", "Transport", "Cable code", "Cable name", "Order length, m", "Cable mass, kg/m", "Cable outer diameter, mm", "Conductor count", "Max production length, m", "Calculate", "Add", "Delete", "Cancel", "Confirm delete", "Reel", "Length per reel, m", "Reel count", "Netto 1 reel, kg", "Brutto 1 reel, kg", "Netto total, kg", "Brutto total, kg", "Bending radius, mm", "No reel can hold this cable within the max production length", "Reel max load exceeded", "Transport max load exceeded", "Settings", "Light", "Dark", "System", "Created by", "Beta".

- [ ] **Step 3: Compile**

```bash
uv run python manage.py compilemessages
```

- [ ] **Step 4: Verify**

Run: `uv run python manage.py shell -c "import django; django.setup(); from django.utils.translation import activate, gettext as _; activate('ru'); print(_('Calculate'))"`
Expected: the Russian translation of "Calculate".

- [ ] **Step 5: Commit**

```bash
git add locale/
git commit -m "i18n: add en/az/ru/tr .po translations"
```

### Task 3.6: i18n tests

**Files:**

- Create: `app/tests/test_i18n.py`

**Interfaces:** Consumes URL routing per language; `set_language`.

- [ ] **Step 1: Write tests**

```python
from django.test import TestCase, override_settings
from django.urls import reverse


class I18nRoutingTests(TestCase):
    def test_default_redirects_to_prefixed(self):
        resp = self.client.get("/")
        self.assertIn(resp.status_code, (302, 301))
        self.assertTrue(resp["Location"].startswith(("/en", "/az", "/ru", "/tr")))

    def test_en_home_renders(self):
        resp = self.client.get("/en/")
        self.assertEqual(resp.status_code, 200)

    def test_each_language_home_renders(self):
        for lang in ("en", "az", "ru", "tr"):
            resp = self.client.get(f"/{lang}/")
            self.assertEqual(resp.status_code, 200, lang)
```

- [ ] **Step 2: Run tests** (after Phase 4 templates render)

Run: `uv run python manage.py test app.tests.test_i18n -v2`
Expected: all pass.

- [ ] **Step 3: Commit**

```bash
git add app/tests/test_i18n.py
git commit -m "test(i18n): per-language routing and rendering"
```

---

## Phase 4 — Design Rebuild (fresh Bootstrap 5.3 + custom design system)

> Invoke the **frontend-design** skill at the start of this phase for design-quality guidance, then implement. All templates use `{% load i18n %}` and `{% trans %}` (merging Task 3.4). No inline styles. No jQuery.

### Task 4.1: Vendor Bootstrap Icons locally

**Files:**

- Create: `crc/static/icons/bootstrap-icons.css` and font files (`bootstrap-icons.woff2`, `.woff`, `.ttf`) under `crc/static/icons/fonts/`

**Interfaces:** Produces a local icon font (no CDN). Fix the CSS `url()` to point to `../fonts/`.

- [ ] **Step 1: Download Bootstrap Icons 1.x** distribution (CSS + fonts) from the official release zip; place CSS at `crc/static/icons/bootstrap-icons.css` and fonts at `crc/static/icons/fonts/`. Fix `@font-face src: url("./fonts/…")` → `url("../fonts/…")` to match the directory layout (CSS in `icons/`, fonts in `icons/fonts/`).

- [ ] **Step 2: Verify the files exist**

Run: `ls crc/static/icons/bootstrap-icons.css crc/static/icons/fonts/bootstrap-icons.woff2`

- [ ] **Step 3: Commit**

```bash
git add crc/static/icons/
git commit -m "feat(ui): vendor Bootstrap Icons locally"
```

### Task 4.2: Add favicon; keep logos

**Files:**

- Create: `crc/static/img/favicon.svg` (derive from `crc-logo-mini.svg`)
- Modify (later): `templates/base.html` to reference it (Task 4.5)

- [ ] **Step 1: Create `favicon.svg`** — copy `crc/static/img/crc-logo-mini.svg` to `crc/static/img/favicon.svg` (or craft a simple monogram).

- [ ] **Step 2: Commit**

```bash
git add crc/static/img/favicon.svg
git commit -m "feat(ui): add favicon"
```

### Task 4.3: Write the design system CSS (`app.css`)

**Files:**

- Create: `crc/static/css/app.css`

**Interfaces:** Produces a token layer + component styles. Light under `:root`/`[data-bs-theme=light]`, dark under `[data-bs-theme=dark]`. Overrides the Bootstrap primary to a diversified brand palette.

- [ ] **Step 1: Write `crc/static/css/app.css`** — a focused design system (the frontend-design skill should guide the exact palette; the structure below is the contract). Key tokens:

```css
:root,
[data-bs-theme="light"] {
  --crc-primary: #0a7d5c;        /* deep teal-green: cables/industry */
  --crc-primary-rgb: 10, 125, 92;
  --crc-accent:   #e07a1f;       /* warm amber accent */
  --crc-accent-rgb: 224, 122, 31;
  --crc-surface:  #ffffff;
  --crc-surface-2:#f6f8f7;
  --crc-border:   #dde3e0;
  --crc-text:     #15201c;
  --crc-muted:    #5b6b64;

  --bs-primary: var(--crc-primary);
  --bs-primary-rgb: var(--crc-primary-rgb);
  --bs-link-color: var(--crc-primary);
  --bs-link-hover-color: var(--crc-accent);
  --bs-body-bg: var(--crc-surface);
  --bs-body-color: var(--crc-text);
  --bs-border-color: var(--crc-border);
}

[data-bs-theme="dark"] {
  --crc-primary: #2fbf8f;
  --crc-primary-rgb: 47, 191, 143;
  --crc-accent:   #f4a23a;
  --crc-accent-rgb: 244, 162, 58;
  --crc-surface:  #0f1513;
  --crc-surface-2:#161f1c;
  --crc-border:   #233029;
  --crc-text:     #e7efea;
  --crc-muted:    #9bb0a6;

  --bs-primary: var(--crc-primary);
  --bs-primary-rgb: var(--crc-primary-rgb);
  --bs-link-color: var(--crc-primary);
  --bs-link-hover-color: var(--crc-accent);
  --bs-body-bg: var(--crc-surface);
  --bs-body-color: var(--crc-text);
  --bs-border-color: var(--crc-border);
}

/* Buttons */
.btn-primary { --bs-btn-bg: var(--crc-primary); --bs-btn-border-color: var(--crc-primary);
  --bs-btn-hover-bg: var(--crc-accent); --bs-btn-hover-border-color: var(--crc-accent);
  --bs-btn-active-bg: var(--crc-primary); color: #fff; }
.btn-ghost { background: transparent; color: var(--crc-text); border: 1px solid var(--crc-border); }
.btn-ghost:hover { background: var(--crc-surface-2); }

/* Layout */
.app-shell { display: flex; min-height: 100vh; }
.app-sidebar { width: 250px; background: var(--crc-surface-2); border-right: 1px solid var(--crc-border); }
.app-main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
.app-content { padding: 1.25rem; flex: 1; }
.app-navbar { background: var(--crc-surface); border-bottom: 1px solid var(--crc-border); }

/* Tables */
.app-table { width: 100%; border-collapse: separate; border-spacing: 0; }
.app-table thead th { position: sticky; top: 0; background: var(--crc-surface-2); z-index: 2; }
.app-table tbody tr:nth-child(even) { background: var(--crc-surface-2); }
.app-table tbody tr:hover { background: color-mix(in srgb, var(--crc-primary) 8%, var(--crc-surface)); }
.table-scroll { max-height: 70vh; overflow: auto; }

/* Cards */
.app-card { background: var(--crc-surface); border: 1px solid var(--crc-border); border-radius: .65rem; }
.app-card-header { padding: .75rem 1rem; border-bottom: 1px solid var(--crc-border); font-weight: 600; }
.app-card-body { padding: 1rem; }

/* Fill bar (drum utilization visualization) */
.fill-bar { height: 10px; background: var(--crc-surface-2); border-radius: 6px; overflow: hidden; }
.fill-bar > span { display: block; height: 100%; background: var(--crc-primary); }

/* Focus & a11y */
:focus-visible { outline: 3px solid color-mix(in srgb, var(--crc-primary) 45%, transparent); outline-offset: 2px; }

/* Responsive */
@media (max-width: 768px) {
  .app-sidebar { display: none; }
  .app-table { font-size: .85rem; }
}
```

- [ ] **Step 2: Commit**

```bash
git add crc/static/css/app.css
git commit -m "feat(ui): custom design system tokens, components, light/dark"
```

### Task 4.4: Write `app.js` (theme switcher, formset rows, lang) — vanilla JS

**Files:**

- Create: `crc/static/js/app.js`

**Interfaces:** Produces: theme apply/remember; formset add/remove row (updates `TOTAL_FORMS`); language switcher submit.

- [ ] **Step 1: Write `crc/static/js/app.js`**:

```javascript
// Theme switcher
(function () {
  function resolvedTheme() {
    var saved = localStorage.getItem("crc-theme");
    if (saved === "light" || saved === "dark") return saved;
    return window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }
  function applyTheme(t) {
    document.documentElement.setAttribute("data-bs-theme", t);
    localStorage.setItem("crc-theme", t);
    var toggle = document.getElementById("theme-toggle");
    if (toggle) toggle.setAttribute("aria-pressed", t === "dark");
  }
  window.crcApplyTheme = applyTheme;
  document.addEventListener("DOMContentLoaded", function () {
    applyTheme(resolvedTheme());
    var toggle = document.getElementById("theme-toggle");
    if (toggle) toggle.addEventListener("click", function () {
      var cur = document.documentElement.getAttribute("data-bs-theme");
      applyTheme(cur === "dark" ? "light" : "dark");
    });
  });
})();

// Formset row management (cable_cal form)
(function () {
  function totalFormInput(form) {
    return form.querySelector("input[name$='-TOTAL_FORMS']");
  }
  document.addEventListener("click", function (e) {
    var addBtn = e.target.closest("[data-formset-add]");
    if (!addBtn) return;
    var form = document.getElementById(addBtn.getAttribute("data-formset-add"));
    var total = totalFormInput(form);
    var idx = parseInt(total.value, 10);
    var tpl = form.querySelector("[data-formset-empty]");
    var row = tpl.cloneNode(true);
    row.removeAttribute("data-formset-empty");
    row.classList.remove("d-none");
    row.innerHTML = row.innerHTML.replace(/__prefix__/g, String(idx));
    tpl.parentNode.insertBefore(row, tpl);
    total.value = idx + 1;
    e.preventDefault();
  });
  document.addEventListener("click", function (e) {
    var delBtn = e.target.closest("[data-formset-delete]");
    if (!delBtn) return;
    var row = delBtn.closest("[data-formset-row]");
    if (!row) return;
    var delInput = row.querySelector("input[name$='-DELETE']");
    if (delInput) { delInput.checked = true; row.classList.add("d-none", "opacity-50"); }
    else { row.remove(); }
    e.preventDefault();
  });
})();
```

- [ ] **Step 2: Commit**

```bash
git add crc/static/js/app.js
git commit -m "feat(ui): vanilla JS theme switcher + formset row management"
```

### Task 4.5: Rewrite `templates/base.html` + partials

**Files:**

- Rewrite: `templates/base.html`
- Create: `templates/partials/_theme_init.html`, `_navbar.html`, `_sidebar.html`, `_footer.html`, `_lang_switcher.html`

**Interfaces:** Produces the shell: `<html lang="{{ LANGUAGE_CODE }}" data-bs-theme="…">`, Bootstrap + app.css + Bootstrap Icons + app.js, theme init script in `<head>`, navbar with theme toggle + language switcher, sidebar nav, content block, footer.

- [ ] **Step 1: Write `templates/partials/_theme_init.html`** (inline, before paint):

```html
<script>
  (function () {
    try {
      var t = localStorage.getItem("crc-theme");
      if (!t) t = window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
      document.documentElement.setAttribute("data-bs-theme", t);
    } catch (e) {}
  })();
</script>
```

- [ ] **Step 2: Write `templates/partials/_lang_switcher.html`**:

```html
{% load i18n %}
<form action="{% url 'set_language' %}" method="post" class="d-inline">
  {% csrf_token %}
  <input name="next" type="hidden" value="{{ request.get_full_path }}">
  <select name="language" class="form-select form-select-sm" onchange="this.form.submit()" aria-label="{% trans 'Language' %}">
    {% get_current_language as LANGUAGE_CODE %}
    {% get_available_languages as LANGUAGES %}
    {% for code, name in LANGUAGES %}
      <option value="{{ code }}" {% if code == LANGUAGE_CODE %}selected{% endif %}>{{ name }}</option>
    {% endfor %}
  </select>
</form>
```

- [ ] **Step 3: Write `templates/partials/_navbar.html`**, `_sidebar.html`, `_footer.html`** using `{% trans %}` for all labels. Sidebar links use `app:` namespaced `{% url %}`. Theme toggle button: `<button id="theme-toggle" class="btn btn-ghost" aria-pressed="false" aria-label="{% trans 'Toggle theme' %}"><i class="bi bi-circle-half"></i></button>`.

- [ ] **Step 4: Write `templates/base.html`**:

```html
{% load i18n static %}
<!DOCTYPE html>
<html lang="{{ LANGUAGE_CODE|default:'en' }}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{% block title %}{% trans "Cable Reels Calculator" %}{% endblock %}</title>
  {% include "partials/_theme_init.html" %}
  <link rel="stylesheet" href="{% static 'bootstrap/css/bootstrap.min.css' %}">
  <link rel="stylesheet" href="{% static 'icons/bootstrap-icons.css' %}">
  <link rel="stylesheet" href="{% static 'css/app.css' %}">
  <link rel="icon" href="{% static 'img/favicon.svg' %}" type="image/svg+xml">
</head>
<body>
  <div class="app-shell">
    {% include "partials/_sidebar.html" %}
    <div class="app-main">
      {% include "partials/_navbar.html" %}
      <main class="app-content">
        {% if messages %}
          {% for m in messages %}<div class="alert alert-{{ m.tags|default:'info' }} alert-dismissible fade show" role="alert">{{ m }}<button type="button" class="btn-close" data-bs-dismiss="alert"></button></div>{% endfor %}
        {% endif %}
        {% block content %}{% endblock %}
      </main>
      {% include "partials/_footer.html" %}
    </div>
  </div>
  <script src="{% static 'bootstrap/js/bootstrap.bundle.min.js' %}"></script>
  <script src="{% static 'js/app.js' %}"></script>
  {% block scripts %}{% endblock %}
</body>
</html>
```

- [ ] **Step 5: Verify render**

Run: `uv run python manage.py runserver` → open `/en/` in a browser; confirm navbar, sidebar, theme toggle, language switcher work; toggle dark/light; switch language.

- [ ] **Step 6: Commit**

```bash
git add templates/
git commit -m "feat(ui): rebuild base template with design system, theme + lang switchers, i18n"
```

### Task 4.6: Rewrite `cable_cal.html` (formset entry)

**Files:**

- Rewrite: `app/templates/app/cable_cal.html`

**Interfaces:** Consumes `form` (CableCalForm) + `formset` (CableLineItemFormSet). Renders the management form, a table of line-item forms, an empty row template (`data-formset-empty`) for JS cloning, and add/remove buttons. All text `{% trans %}`.

- [ ] **Step 1: Write the template** — render `{{ formset.management_form }}`, loop `{{ formset.empty_form }}` as the hidden template with `__prefix__`, and `{{ formset }}` rows. Header fields: order_num + transport + optional overrides. Buttons: `<button data-formset-add="line-form">…</button>` and per-row `<button data-formset-delete>…</button>`. Use `app-table` + `table-scroll`. All visible labels via `{% trans %}`. No inline styles.

- [ ] **Step 2: Verify** — submit a 2-line calculation via the UI; confirm redirect to detail with 2 line items.

- [ ] **Step 3: Commit**

```bash
git add app/templates/app/cable_cal.html
git commit -m "feat(ui): formset-based cable calculation form with i18n"
```

### Task 4.7: Rewrite `cable_cal_list.html`

**Files:**

- Rewrite: `app/templates/app/cable_cal_list.html`

- [ ] **Step 1: Render a table** of `cable_cal` (order_num link via `get_absolute_url`, created_at) with `app-table`, empty-state message `{% trans "No calculations yet." %}`, an "Add" button linking `app:cable_cal`. `{% trans %}` headers.

- [ ] **Step 2: Commit**

### Task 4.8: Rewrite `cable_cal_detail.html` (results with line items)

**Files:**

- Rewrite: `app/templates/app/cable_cal_detail.html`

**Interfaces:** Consumes `cable_cal.line_items` (the new relation). Replaces all `cable_cal.cod|linebreaks` etc. with a table iterating `cable_cal.line_items.all`.

- [ ] **Step 1: Render two tables**: (1) results table per line item (code, name, reel, reel_len, reel_num, netto_1, brutto_1, netto_all, brutto_all, bending_radius, warning badge) with a fill-bar showing `reel_len / max_len` utilization; (2) inputs table (code, name, mass, diameter, con_num, max_len). Delete button → `app:cable_del`. All headers `{% trans %}`. Warning rendered as an amber badge when `item.warning`.

- [ ] **Step 2: Verify** — view one of the 3 migrated calculations; confirm line items render from the new relation.

- [ ] **Step 3: Commit**

```bash
git add app/templates/app/cable_cal_detail.html
git commit -m "feat(ui): results page renders line items + utilization bars + warnings"
```

### Task 4.9: Rename delete-confirm templates; rewrite them

**Files:**

- Rename: `app/templates/app/cable_cal_del.html` → `cable_cal_confirm_delete.html`
- Rename: `reels_del.html` → `reels_confirm_delete.html`, `transport_del.html` → `transport_confirm_delete.html`
- Update `views.py` `template_name` accordingly.

- [ ] **Step 1: Rewrite each** as a simple confirm card: "Delete <name>?" + Cancel + Delete buttons, `{% trans %}`. Fix the delete views' `template_name` to the new names.

- [ ] **Step 2: Commit**

### Task 4.10: Rewrite reels list/detail/add + transport list/detail

**Files:**

- Rewrite: `app/templates/app/reels.html`, `reels_detail.html`, `reels_add.html`, `transport.html`, `transport_detail.html`

**Interfaces:** Fixes invalid `<form>`-in-`<tbody>` (Task 4.11 handles the add form); fixes `transport_add.html` wrong title (Task 4.11).

- [ ] **Step 1: Rewrite list/detail templates** with `app-table`, `table-scroll`, `th scope="col"`, `{% trans %}` headers, "Add" buttons, empty states.

- [ ] **Step 2: Commit**

### Task 4.11: Rewrite `reels_add.html` + `transport_add.html` (fix invalid form nesting + wrong title)

**Files:**

- Rewrite: `app/templates/app/reels_add.html`, `transport_add.html`

- [ ] **Step 1: Put the `<form>` OUTSIDE the `<table>`** (valid HTML): wrap the table in `<form method="post">…</form>`, render fields in `<td>`, submit button below. `transport_add.html` title → `{% trans "Add transport" %}` (not reel). Use `form-control`/`form-select` classes, `{% trans %}` labels, render `{{ form.errors }}` per field.

- [ ] **Step 2: Verify** — submit a new reel and a new transport via the UI; confirm creation.

- [ ] **Step 3: Commit**

```bash
git add app/templates/app/reels_add.html app/templates/app/transport_add.html
git commit -m "fix(ui): valid form nesting; correct transport add title; i18n"
```

### Task 4.12: Remove legacy `CableCal` TextField columns (deferred from Task 2.5 Step 5)

**Files:**

- Modify: `app/models.py` (remove the old fields)
- Create: `app/migrations/0006_remove_cablecal_legacy_columns.py` (generated)

- [ ] **Step 1: Delete the legacy fields** from `CableCal`: `cod, name, mass, diameter, con_num, order_len, max_len, reel_name, reel_type, reel_num, reel_len, bending_radius, netto_1, brutto_1, netto_all, brutto_all`.

- [ ] **Step 2: Make + run migration**

Run: `uv run python manage.py makemigrations app --name remove_cablecal_legacy_columns && uv run python manage.py migrate app`

- [ ] **Step 3: Verify the site still works** (templates now use `line_items`): open detail page of a migrated calc; run full test suite.

Run: `uv run python manage.py test`
Expected: all pass.

- [ ] **Step 4: Commit**

```bash
git add app/models.py app/migrations/
git commit -m "refactor: remove legacy newline-joined CableCal text columns"
```

### Task 4.13: Lint templates — no inline styles, no `<h7>`, no hardcoded AZ

**Files:** all templates.

- [ ] **Step 1: Grep for regressions**

Run:

```bash
grep -rnE 'style="|<h7|style=' templates/ app/templates/ && echo "FOUND INLINE STYLE / h7" || echo "clean"
grep -rnE 'Sifariş|Baraban|Kabel|Hesablama|Nəqliyyat|Əlavə|Hesabla' templates/ app/templates/ && echo "FOUND HARDCODED AZ" || echo "clean"
```

Expected: both "clean". Fix any hits.

- [ ] **Step 2: Commit** (if changes) `git commit -am "lint: remove leftover inline styles / hardcoded strings"`.

---

## Phase 5 — Finalize

### Task 5.1: Admin improvements

**Files:**

- Modify: `app/admin.py`

- [ ] **Step 1: Add `CableLineItemInline`** (TabularInline) on `CableCalAdmin`; register `CalculationSettingsAdmin` (single row; restrict add/delete). Use `gettext_lazy` (already via model).

- [ ] **Step 2: Verify** — open `/admin/`; confirm inline renders, settings singleton editable.

- [ ] **Step 3: Commit**

### Task 5.2: Run i18n extraction now that all templates are marked (Task 3.5)

Execute Task 3.5 (makemessages + fill translations + compilemessages) now.

### Task 5.3: Full verification & smoke

- [ ] **Step 1: Full test suite**

Run: `uv run python manage.py test -v2`
Expected: all pass.

- [ ] **Step 2: Checks**

Run: `uv run python manage.py check --deploy` (note warnings acceptable for dev; fix `SECURITY` ones that are cheap).

- [ ] **Step 3: collectstatic**

Run: `uv run python manage.py collectstatic --noinput` → confirm `static/` builds and is gitignored.

- [ ] **Step 4: Manual smoke** — runserver; walk all 4 languages × light/dark; create a calculation; view list/detail; add/delete reel & transport.

- [ ] **Step 5: Final commit**

```bash
git add -A
git commit -m "chore: finalize — admin inline, translations, full verification"
```

---

## Self-Review Checklist (run before handoff)

- **Spec coverage:** every audit finding (A1–5, B6, C7–11, D12–22, E23–25, F26, G27–33, i18n 53–54, design 50–52) maps to a task above. (Audit findings list lives in the chat audit summary; this plan addresses each: Phase 0 = A/B/infra; Phase 1 = D/E/F; Phase 2 = C; Phase 3 = i18n; Phase 4 = G/design; Phase 5 = admin/docs.)
- **Placeholder scan:** no "TBD"/"implement later". The `reel_num` assertion in Task 2.7 has an explicit compute-and-fill instruction (not a placeholder). The `.po` translation in 3.5 lists concrete strings.
- **Type consistency:** `LineResult` field names (`reel_pk`, `reel_name`, `reel_len`, `reel_num`, `netto_1`, `brutto_1`, `netto_all`, `brutto_all`, `bending_radius`, `warning`) match usage in `compute_line` (1.1), the view (2.4), and the detail template (4.8). `CalculationSettings` fields match `get_solo` (2.1) and view usage (2.4). URL names match between `app/urls.py` (1.4) and templates/models (`app:` namespace).
- **Ordering dependency:** Task 2.5 Step 5 deferred to Task 4.12 — noted in both. Task 3.4 merged into Phase 4 — noted. Task 3.5 runs at 5.2 — noted.

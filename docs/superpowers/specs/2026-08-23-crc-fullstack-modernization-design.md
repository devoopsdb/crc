# CRC Full-Stack Modernization — Design Spec

**Date:** 2026-08-23
**Project:** CRC — Cable Reels Calculator (Django 6.1, Python 3.13)
**Status:** Approved (decisions confirmed 2026-08-23)

> This spec is the source of truth for the implementation plan
> `docs/superpowers/plans/2026-08-23-crc-fullstack-modernization.md`.
> The plan argues from this spec.

---

## 1. Context

CRC is a single-purpose internal web app that calculates how much cable fits on
each drum/reel in a cable order, how many reels are needed, and net/gross
weights, then checks transport feasibility. Stack today: Django 6.1 (just
upgraded from 5.1) + Bootstrap 5.3.3 + jQuery 3.6 + the "Star Admin" admin
template, SQLite, all UI text hardcoded in Azerbaijani.

A full audit found critical bugs in the winding formula, a broken `.gitignore`
that drops migrations from git, version-config conflicts, an anti-relational
data model (multi-row numeric data stored as newline-joined `TextField`s),
invalid HTML in forms, dead code, and missing i18n/theming infrastructure.

## 2. Goals

1. **Stabilize** the project on Django 6.1 with correct, reproducible config.
2. **Fix all critical backend/formula bugs** with test coverage.
3. **Normalize the data model** (`CableCal` header + `CableLineItem` rows).
4. **Add 4-language i18n** (en, az, ru, tr) via path-based `i18n_patterns`.
5. **Rebuild the frontend** on fresh local Bootstrap 5.3 with a custom design
   system: diversified palette, light/dark themes + switcher, best-practice
   UI/UX, no jQuery.
6. **Review & correct the winding formula** with configurable, guarded logic.
7. Leave the codebase clean: no dead code, no debug leftovers, tests green.

## 3. Non-Goals

- No authentication / login (decision 4: keep all views public).
- No `.env` file or `django-environ` dependency (decision 5).
- No REST API / SPA rewrite (server-rendered Django templates stay).
- No change of database (SQLite stays).
- No CI/CD pipeline setup (out of scope; lint config optional).

## 4. Confirmed Decisions

| # | Decision | Choice |
| --- | ---------- | -------- |
| 1 | i18n URL strategy | Path-based via `i18n_patterns` (`/en/`, `/az/`, `/ru/`, `/tr/`) |
| 2 | Data model depth | Full normalization: `CableCal` + `CableLineItem` + data migration |
| 3 | Formula params | Global `CalculationSettings` (defaults) + optional per-calc override |
| 4 | Auth | None — all views public |
| 5 | Env config | stdlib `os.environ.get()` with safe defaults; **no `.env` file** |
| 6 | Frontend base | Fresh local Bootstrap 5.3.3 + custom design system; drop Star Admin + jQuery |
| 7 | `.gitignore` | Fix: stop ignoring migrations; ignore `static/` (collectstatic output) |
| 8 | UI/UX | Deep best-practice overhaul (a11y, responsive, states, hierarchy) |

## 5. Architecture

### 5.1 Backend / formula

The winding length per reel for one cable line:

```
L (m) = packing * B * (D_wind² - d_core²) / (4 * d_cable²) * (π / 1000)
```

where `D_wind = D_flange - 2 * margin` (margin configurable, default 50 mm per
side → the current hardcoded `100` becomes `2 * margin`), `B` = barrel width
(`length_neck`), `d_core` = `diameter_neck`, `d_cable` = cable outer diameter,
`packing` = filling factor (default 0.93). The formula keeps the "turns"
convention (π/4 form) the project already uses; the spec records this so the
company can later swap the convention by changing `packing`/constants in one
place. **Guards required**: `D_wind > d_core`, `d_cable <= B`, `d_cable > 0`,
`reel_count = ceil(order_len / L_per_reel)` (never `round`), `reel_count >= 1`,
and **max_load checks** for both the chosen reel and the transport. When no reel
fits a line, raise a user-visible error (never the silent `append(1)` fallback).

Configuration lives in a `CalculationSettings` singleton model (one active row)
with fields: `winding_margin_mm` (default 50), `packing_factor` (default 0.93),
`use_flange_height` (bool, default False). Each `CableCal` may optionally store
an override snapshot (`margin_override`, `packing_override`, nullable) so a
saved calculation is reproducible even if global defaults change later.

`bending_radius`: computed from cable diameter × a multiplier (configurable,
default per common practice e.g. `10 * d_cable` for power cables) and stored on
the line item, OR the field is removed. Implementation will populate it; if no
multiplier is supplied we keep a sensible default and make it a
`CalculationSettings` field.

### 5.2 Data model

- `CableCal` (order header): `order_num` (unique), `transport` FK, timestamps,
  optional `margin_override`, `packing_override`, `notes`. Drops the
  newline-joined `TextField` columns.
- `CableLineItem` (new, FK→`CableCal`, ordered): `position`, `cod`, `name`,
  `con_num` (int), `order_len` (Decimal, m), `max_len` (Decimal, m),
  `mass` (Decimal, kg/m), `diameter` (Decimal, mm), plus computed result
  columns: `reel` FK→`ReelsList` (chosen reel), `reel_len` (Decimal, m per
  reel), `reel_num` (int), `netto_1`, `brutto_1`, `netto_all`, `brutto_all`
  (Decimal kg), `bending_radius` (Decimal, mm), `warning` (text, blank).
- `ReelsList`, `ReelType`, `TransportList`: keep, convert any remaining
  numeric `TextField`s; add `CheckConstraint`s (`diameter > diameter_neck`,
  `max_load > 0`, `length_neck > 0`).
- **Data migration**: split the 3 existing `CableCal` records' newline-joined
  fields into `CableLineItem` rows; preserve computed result columns. Run in a
  single `RunPython` migration with a reverse `RunPython.noop`.

### 5.3 i18n

- `LANGUAGES = [("en","English"),("az","Azərbaycanca"),("ru","Русский"),("tr","Türkçe")]`,
  `LANGUAGE_CODE = "en"`, `USE_I18N = True`, `LOCALE_PATHS = [BASE_DIR/"locale"]`.
- `LocaleMiddleware` added after `SessionMiddleware`, before `CommonMiddleware`.
- `i18n_patterns(include("app.urls"), prefix_default_language=True)` under each
  language prefix; admin stays under `/admin/` (not prefixed) per common
  practice, or prefixed — plan will prefix admin too for consistency.
- All UI strings → `{% trans %}` / `{% blocktrans %}`; model `verbose_name` /
  form labels / error messages → `gettext_lazy`.
- Language switcher in navbar → posts/links to `set_language` or a custom view
  that redirects back with the chosen prefix; choice persisted in session +
  `django_language` cookie (Django default behavior).
- `makemessages -l en -l az -l ru -l tr` → `.po` files committed; `.mo`
  compiled (gitignored, already is). Initial translations provided for all 4.
- All 4 languages are LTR → no RTL work.

### 5.4 Frontend / design

- Base: local Bootstrap 5.3.3 (already vendored in `crc/static/bootstrap/`).
  Remove Star Admin `style.css` (536 KB), `vendor.bundle.base.css/js`,
  `themify-icons.css`, jQuery, all unused dashboard/chart JS. Add Bootstrap
  Icons (local) for iconography.
- Custom design system in a new `crc/static/css/app.css` built on Bootstrap
  CSS custom properties (`--bs-*`) + a proprietary token layer
  (`--crc-primary`, `--crc-accent`, `--crc-surface-*`, `--crc-text-*`,
  `--crc-border`, …) defined under `:root` (light) and `[data-bs-theme="dark"]`
  (dark). Diversified palette: a primary brand color + accent + neutral scale.
- Themes via Bootstrap 5.3 color modes: `<html data-bs-theme="light|dark">`.
  Switcher in navbar: toggle + persist to `localStorage`; a tiny inline script
  in `<head>` applies the stored theme before paint (no flash); a Django
  cookie mirrors it for server-rendered initial state. Respect
  `prefers-color-scheme` on first visit.
- No inline `style="..."` in templates — all styling via utility classes /
  component classes in `app.css`.
- UI/UX best practices: clear heading hierarchy (h1–h6 only, no h7), sticky
  table headers with horizontal scroll on mobile, zebra rows, hover states,
  visible focus rings, `aria-label`s on icon buttons, `<th scope="col">`,
  form validation feedback (Django form errors rendered), empty/loading/error
  states, toast/notification for calc result + any warnings, a results page
  with per-line drum allocation + a simple fill-bar visualization, consistent
  button system (primary/danger/ghost), responsive layout, footer.
- Form entry uses a Django **formset** (`CableLineItemFormSet`) with proper
  management form; add/remove rows via accessible buttons wired with vanilla
  JS that clones a template row and updates `TOTAL_FORMS`/`FORMS` — no
  duplicate element IDs.

### 5.5 Infra / config

- `requirements.txt` synced to `uv.lock` (Django 6.1, asgiref 3.12.1, sqlparse
  0.6.0) **or removed** in favor of `uv` only; README rewritten (Python 3.13,
  Django 6.1, uv workflow). **Decision: keep `requirements.txt` synced** (some
  users still pip) AND document uv.
- `settings.py`: stdlib `os.environ.get()` for `SECRET_KEY`, `DEBUG`,
  `ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS` with safe defaults (no `.env` file);
  update all doc comments `5.0` → `6.1`; modernize to `STORAGES` dict; keep
  `DEFAULT_AUTO_FIELD`; `LOCALE_PATHS`; `LANGUAGES`.
- `.gitignore`: remove `**/migrations/*.py` rule so migrations are committed;
  add `/static/` (STATIC_ROOT collectstatic output); keep `.venv/`, `db.sqlite3`,
  `*.mo`. Commit existing migrations 0001–0003 (then new ones from refactor).
- Remove duplicate committed `static/` tree (keep `crc/static/` sources).
- Remove dead code: `cal_cable.html`, `tessst.html`, `x` view + `x/` route,
  `main.py` stub, unused JS files, `print()` debug, dead `clean_title`,
  `ReelType.get_absolute_url` crash fix.

## 6. Testing Strategy

- **Unit tests** for the winding formula (`app/calc.py` pure functions): given
  reel + cable + settings → expected `L`, `reel_num` (ceil), weights; guard
  cases (no fit, div-by-zero, negative geometry, overload).
- **Model tests**: `CableLineItem` creation, constraints, `CalculationSettings`
  singleton/defaults.
- **View tests**: formset submission creates header + N line items with correct
  results; error path when no reel fits; list/detail/delete; i18n URLs resolve
  per language; `set_language` redirects.
- **Template/i18n tests**: a test that greps rendered output for expected
  translated strings per language; a check that no hardcoded Azerbaijani
  literals remain in templates (lint-style test).
- **Frontend**: manual visual smoke (light/dark, 4 langs, responsive) +
  `lens_diagnostics`/LSP checks; HTML validity for the form pages.
- Run `python manage.py test` (or `uv run pytest` if we add pytest — decision:
  stick with Django's test runner to avoid new deps).

## 7. Sequencing Rationale

Phases are ordered so each is independently testable and low-regret:

0. **Foundation** — config/gitignore/dead-code (no behavior change, unblocks CI-like reproducibility).
1. **Formula & critical backend bugs** — with tests, before model change so logic is proven.
2. **Model normalization** — data migration of the 3 real records.
3. **i18n** — strings are stable after Phases 1–2 (avoids re-marking churn).
4. **Design rebuild** — templates are stable after i18n marking.
5. **Finalize** — admin, docs, full test run, smoke.

Reversing 3 and 4 would force re-marking strings after template rewrites.
Reversing 1 and 2 would make formula tests depend on the new model.

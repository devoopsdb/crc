# 🧩 CRC — Cable Reels Calculator

> A web application that calculates cable-reel (drum) winding parameters for cable orders — how much cable fits on each reel, how many reels are needed, net/gross weights, the bending radius, and transport-load feasibility.

[![Python](https://img.shields.io/badge/python-3.13+-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Django](https://img.shields.io/badge/Django-6.1-092E20?logo=django&logoColor=white)](https://www.djangoproject.com/)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)](https://getbootstrap.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)
[![uv](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/uv/main/assets/badge/v0.json)](https://docs.astral.sh/uv/)

Built with **Django 6.1** and a custom **Bootstrap 5.3** design system, featuring
**light/dark themes** and a **4-language interface** — English, Azərbaycanca,
Русский, Türkçe.

---

## 📑 Table of Contents

- [✨ Features](#-features)
- [🧠 How it works](#-how-it-works)
- [🚀 Quick Start (uv)](#-quick-start-uv)
- [📦 Alternative: pip](#-alternative-pip)
- [⚙️ Configuration](#-configuration)
- [🌍 Languages & Themes](#-languages--themes)
- [🗂️ Project Structure](#-project-structure)
- [🧪 Testing](#-testing)
- [🚢 Production Deployment](#-production-deployment)
- [🌐 Internationalization](#-internationalization)
- [🤝 Contributing](#-contributing)
- [📄 License](#-license)
- [🙏 Credits](#-credits)

---

## ✨ Features

- **Multi-line cable order entry** with automatic reel selection per line, via a dynamic Django formset (add/remove rows without a page reload).
- **Guarded winding formula** extracted into a pure, unit-tested module (`app/calc.py`) — configurable winding margin, packing factor, and bending-radius multiplier.
- **Safety checks**: reel & transport max-load validation, winding-diameter vs. core checks, and a user-facing error (never a silent crash) when a cable won't fit.
- **Calculation history** with per-line results and a reel-fill visualization.
- **Reference data CRUD** for reels/drums and transport vehicles, with database constraints (diameter > core, positive loads).
- **Light / dark theme** switcher (remembered per browser, respects `prefers-color-scheme`).
- **4 languages** via path-based URLs (`/en/`, `/az/`, `/ru/`, `/tr/`).
- **No external runtime dependencies** beyond Django — Bootstrap, Bootstrap Icons, and the IBM Plex Sans typeface are all vendored locally.

## 🧠 How it works

For each cable line in an order, the app computes the length that fits on every
available reel and picks the one that holds the most cable (fewest reels needed):

```
L (m) = packing · B · (D_wind² − d_core²) / (4 · d_cable²) · π / 1000
```

where `D_wind = reel_diameter − 2·margin`, `B` is the barrel width, `d_core` the
core diameter, and `d_cable` the cable outer diameter. Reel count uses
`ceil(order_len / L)` (never rounds to zero). The margin and packing factor are
editable as global **Calculation settings** (admin) and can be overridden
per calculation for reproducibility.

## 🚀 Quick Start (uv)

[uv](https://docs.astral.sh/uv/) is the recommended, fastest way to run CRC.

```bash
git clone https://github.com/devoopsdb/crc.git
cd crc
uv sync                       # create the venv and install dependencies
uv run python manage.py migrate
uv run python manage.py createsuperuser   # optional — for the admin at /admin/
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000> — you'll be redirected to your language prefix
(e.g. `/en/`). Use the **language selector** and **theme toggle** in the navbar.

## 📦 Alternative: pip

```bash
git clone https://github.com/devoopsdb/crc.git
cd crc
python -m venv .venv
.venv\Scripts\activate             # Windows
# source .venv/bin/activate        # Linux / macOS
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## ⚙️ Configuration

Settings are driven by **environment variables** (no `.env` file required) with
safe defaults for local development.

| Variable | Default | Purpose |
| -------- | ------- | ------- |
| `DJANGO_SECRET_KEY` | built-in dev key | Django secret key — **set a strong value in production** |
| `DJANGO_DEBUG` | `True` | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost,10.1.65.92` | Comma-separated allowed hosts |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `http://127.0.0.1,http://localhost` | Comma-separated trusted origins |

Winding defaults (margin 50 mm/side, packing factor 0.93, bending radius
×10 the cable diameter) are editable via the **Calculation settings** singleton
in the admin, and can be overridden per calculation.

## 🌍 Languages & Themes

- Switch languages with the selector in the navbar — URLs are prefixed
  (`/en/…`, `/az/…`, `/ru/…`, `/tr/…`) and your choice is remembered.
- Toggle the theme with the sun/moon button — light/dark is remembered and
  respects your OS preference on first visit.

## 🗂️ Project Structure

```
crc/
├─ app/                 # calculation app
│  ├─ calc.py           # pure, guarded winding formula (unit-tested)
│  ├─ models.py         # CableCal, CableLineItem, CalculationSettings, ReelsList…
│  ├─ forms.py          # formset for cable line items
│  ├─ views.py          # formset-driven calculation view + CRUD views
│  ├─ admin.py          # inline line items + settings singleton
│  └─ templates/app/    # page templates (i18n, design system)
├─ crc/                 # project settings & root URLs (i18n_patterns)
│  └─ static/            # vendored Bootstrap 5.3, Icons, IBM Plex Sans, app.css/js
├─ templates/            # base shell + partials (sidebar, navbar, theme init)
├─ locale/               # az / ru / tr translation catalogs (.po)
├─ tools/                # build scripts (make_translations.py)
├─ docs/superpowers/      # design spec & implementation plan
└─ manage.py
```

## 🧪 Testing

```bash
uv run python manage.py test
```

The suite covers the winding formula and its guards, the data-model
constraints, and the formset-driven calculation view (success + no-fit error
paths).

## 🚢 Production Deployment

```bash
uv run python manage.py collectstatic --noinput
# Serve with gunicorn/uvicorn behind a reverse proxy.
# In production set: DJANGO_DEBUG=False, a strong DJANGO_SECRET_KEY,
# DJANGO_ALLOWED_HOSTS, and DJANGO_CSRF_TRUSTED_ORIGINS via environment variables.
```

The development SQLite database is **not** tracked in version control — run
`migrate` to create it. For production, configure a robust database
(PostgreSQL recommended) in `DATABASES`.

## 🌐 Internationalization

Translations are authored as a single source in
[`tools/make_translations.py`](tools/make_translations.py), which generates the
`locale/<lang>/LC_MESSAGES/django.po` catalogs and compiles the `.mo` files —
no GNU `gettext` toolchain required.

```bash
uv run python tools/make_translations.py   # edit translations in the script, then re-run
```

To add a language: add its code to `LANGUAGES` in `crc/settings.py`, add a
`{code: name}` entry and a `Plural-Forms` line in the script, and re-run it.

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository and create a branch: `git checkout -b feat/your-feature`.
2. Follow the existing code style (Conventional Commits).
3. Add or update tests for your changes: `uv run python manage.py test`.
4. Run `uv run python manage.py check` before committing.
5. Open a Pull Request describing the change.

The full modernization design and step-by-step plan live under
[`docs/superpowers/`](docs/superpowers/).

## 📄 License

Distributed under the **MIT License**. See [LICENSE](LICENSE) for details.

## 🙏 Credits

- Django · <https://www.djangoproject.com/>
- Bootstrap 5.3 · <https://getbootstrap.com/>
- Bootstrap Icons · <https://icons.getbootstrap.com/>
- IBM Plex Sans · <https://github.com/IBM/plex>
- Original author: [Murad](https://www.linkedin.com/in/murad-h-253bb5223)

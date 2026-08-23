# 🧩 CRC — Cable Reels Calculator

A web application that calculates cable-reel (drum) winding parameters for cable
orders: how much cable fits on each reel, how many reels are needed, net/gross
weights, bending radius, and transport load feasibility.

Built with **Django 6.1** and a custom **Bootstrap 5.3** design system with
light/dark themes and a 4-language interface (English, Azerbaijani, Russian,
Turkish).

## ✨ Features

- Multi-line cable order entry with automatic reel selection per line
- Guarded winding formula (configurable margin & packing factor) with
  max-load checks for reels and transport
- Calculation history with per-line results and utilization indicators
- Reel and transport reference lists (CRUD)
- Light / dark theme switcher (remembered per browser)
- 4 languages via path-based URLs (`/en/`, `/az/`, `/ru/`, `/tr/`)

## 🚀 Quick Start

### Requirements

- Python **3.13+**
- [uv](https://docs.astral.sh/uv/) (recommended) **or** pip

### With uv

```bash
git clone https://github.com/devoopsdb/crc.git
cd crc
uv sync
uv run python manage.py migrate
uv run python manage.py createsuperuser  # optional, for admin
uv run python manage.py runserver
```

Open <http://127.0.0.1:8000> — you will be redirected to your language prefix
(e.g. `/en/`).

### With pip

```bash
git clone https://github.com/devoopsdb/crc.git
cd crc
python -m venv .venv
.venv\Scripts\activate          # Windows
# source .venv/bin/activate     # Linux/macOS
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

## ⚙️ Configuration

Settings are environment-variable driven (no `.env` file required). Defaults
are safe for local development.

| Variable | Default | Purpose |
| ---------- | --------- | --------- |
| `DJANGO_SECRET_KEY` | built-in dev key | Django secret key (set in production) |
| `DJANGO_DEBUG` | `True` | Debug mode |
| `DJANGO_ALLOWED_HOSTS` | `127.0.0.1,localhost,10.1.65.92` | Comma-separated allowed hosts |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | `http://127.0.0.1,http://localhost` | Comma-separated trusted origins |

Winding defaults (margin 50 mm/side, packing factor 0.93, bending radius
multiplier 10×) are editable via the **Calculation settings** singleton in the
admin, and can be overridden per calculation.

## 🌍 Languages & Themes

Use the language selector in the navbar to switch between English, Azerbaijani,
Russian, and Turkish. Use the theme toggle to switch between light and dark
(preferences are remembered).

## 🧪 Tests

```bash
uv run python manage.py test
```

## 📦 Production

```bash
uv run python manage.py collectstatic --noinput
# Serve with gunicorn/uvicorn behind a reverse proxy; set DEBUG=False and
# a strong DJANGO_SECRET_KEY via environment variables.
```

## 📜 License

MIT

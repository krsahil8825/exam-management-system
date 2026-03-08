## Exam Management System

A Django-based platform for managing online exams, candidate registrations, internal workflow, and staff communication.

This repository is structured as a modular backend project with dedicated apps for accounts, exams, communication, and workflow, plus Tailwind integration for frontend styling.

## What this project currently includes

- Custom `User` model (`accounts.User`) with profile support and role-based employee/candidate separation.
- Exam lifecycle models: `Exam`, `Question`, `Registration`, `Answer`, and `Result`.
- Internal staff messaging via the `communication` app.
- Internal task assignment and tracking via the `workflow` app.
- Environment-driven settings for development and production.
- Tailwind CSS setup using `django-tailwind`.
- Production-friendly static file handling with WhiteNoise.

## Tech stack

- Python 3.14+
- Django 6
- django-tailwind 4
- WhiteNoise
- Uvicorn (ASGI)
- SQLite (default) or MySQL (production-ready settings)

## Project apps

- `accounts` — custom authentication model and user profiles (candidate/employee)
- `exams` — exam definitions, questions, registrations, submissions, results
- `communication` — employee-to-employee messaging
- `workflow` — task assignment between employees
- `errors` — custom production error views
- `theme` — Tailwind theme app

## Quick start (local development)

### 1) Install dependencies

```bash
uv sync
```

### 2) Configure environment

Copy development environment template:

```bash
cp .env.dev.example .env
```

On Windows PowerShell:

```powershell
Copy-Item .env.dev.example .env
```

Update values in `.env` if needed (at minimum keep `SECRET_KEY`, `DEBUG`, and `DB_ENGINE`).

### 3) Run migrations

```bash
uv run python manage.py migrate
```

### 4) (Optional) Create superuser

```bash
uv run python manage.py createsuperuser
```

### 5) Start development server

```bash
uv run python manage.py runserver
```

Open:

- Admin: `http://127.0.0.1:8000/admin/`
- Accounts app: `http://127.0.0.1:8000/accounts/`
- Exams app: `http://127.0.0.1:8000/exams/`
- Communication app: `http://127.0.0.1:8000/communication/`
- Workflow app: `http://127.0.0.1:8000/workflow/`

## Tailwind workflow

First-time install:

```bash
uv run python manage.py tailwind install
```

Watch mode (development):

```bash
uv run python manage.py tailwind start
```

Production CSS build:

```bash
uv run python manage.py tailwind build
```

## Environment profiles

- `.env.dev.example` — local development profile (SQLite + debug)
- `.env.production.example` — production profile (MySQL + hardened security settings)

In production mode (`ENV=production` and `DEBUG=False`), the project enables stricter security behavior (secure cookies, HSTS, CSRF trusted origins, SSL redirect, etc.).

## Build and run scripts

The repository includes helper scripts in `_scripts/`:

- Build (Windows): `_scripts/powershell/build.ps1`
- Build (Unix): `_scripts/shell/build.sh`
- Start ASGI server (Windows): `_scripts/powershell/startserver.ps1`
- Start ASGI server (Unix): `_scripts/shell/startserver.sh`

## Notes

- Database file is stored at `_data/db.sqlite3` in local mode.
- Media uploads are stored under `media/`.
- Migrations are currently ignored in `.gitignore` during active development.

## Useful commands

```bash
uv run python manage.py makemigrations
uv run python manage.py migrate
uv run python manage.py collectstatic --noinput
uv run python manage.py test
```

For a larger command reference, see `_scripts/Important_commands.md`.

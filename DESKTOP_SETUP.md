# MyTradeMaster Windows desktop test build

This is a first local desktop wrapper around the existing FastAPI/Jinja2 application. It uses PyWebView to display the app in a desktop window and keeps the existing templates and static files.

## Important scope

- This is a **single-PC/local test setup**: the desktop app runs FastAPI on `127.0.0.1:8765` and connects to the PostgreSQL database specified in `.env`.
- PostgreSQL itself must be installed and running, and the database named in `DATABASE_URL` must already exist.
- On startup, the launcher runs `Base.metadata.create_all()` against the current SQLAlchemy models. It creates missing tables; it does not alter existing tables, run Alembic migrations, seed company/admin records, or migrate old data.
- Do not use `create_all()` as a replacement for schema upgrades on a database that already contains production data.
- The uploaded `.env` file was intentionally excluded because it may contain passwords, tokens, mail credentials, and other secrets. Use `.env.example` as a template and create your own `.env`.

## Test from source on Windows

1. Install Python 3.11 or 3.12, PostgreSQL, and (if rebuilding Tailwind CSS) Node.js.
2. Create an empty PostgreSQL database, for example `mytrademaster_db`.
3. Copy `.env.example` to `.env` and set `DATABASE_URL` to the correct PostgreSQL connection string. Fill any other required settings. Generate a unique `SECRET_KEY`.
4. Run `install_desktop.bat`.
5. Run `run_desktop.bat`.
6. If database initialization or startup fails, inspect `desktop_startup.log`.

## Build a distributable Windows folder

Run `build_windows.bat` after source-mode testing succeeds. It creates `dist\MyTradeMaster\MyTradeMaster.exe` and bundles templates/static files. Copy a correctly configured `.env` beside the executable on the target PC; do not distribute a developer's secret-bearing `.env` file.

## Tailwind CSS

- Development: `npm run dev:css`
- Production CSS build: `npm run build:css`

The compiled `static/css/output.css` is bundled with the app. The end-user does not need to run the Tailwind watcher.

## Current limitations to test before client delivery

- Configure email/SMTP settings if email features are required.
- Confirm printing, PDF/export, and any browser-specific behavior in PyWebView.
- Make sure the client creates a PostgreSQL database and uses a unique secret.
- This wrapper binds only to localhost. For multi-PC LAN use, run FastAPI on the host PC and have other desktop clients connect to that host; do not simply change the bind address without adding firewall and access controls.
